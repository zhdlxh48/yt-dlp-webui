from __future__ import annotations

import asyncio
import os
import signal
import subprocess
import sys
from collections.abc import Awaitable, Callable

from ytdlp_webui.services.process_output import ProcessOutput, ProcessOutputParser

OutputCallback = Callable[[ProcessOutput], Awaitable[None]]


class RunningProcess:
    def __init__(
        self,
        command: list[str],
        process: asyncio.subprocess.Process,
        output_task: asyncio.Task[int],
    ) -> None:
        self.command = command
        self.process = process
        self.output_task = output_task

    @property
    def pid(self) -> int | None:
        return self.process.pid

    async def stop(self, force: bool = False) -> int:
        """프로세스를 종료합니다.

        force=False: SIGINT(Ctrl+C)를 전달하여 yt-dlp가 ffmpeg 병합 후 graceful 종료하도록 합니다.
                     AttachConsole이 실패하면 즉시 force kill합니다.
        force=True:  프로세스 트리 전체를 즉시 kill합니다.
        """
        if self.process.returncode is not None:
            return self.process.returncode

        if not force:
            if await self._send_graceful_interrupt():
                try:
                    # SIGINT 전달 성공 → yt-dlp가 graceful 종료할 때까지 대기
                    # (ffmpeg 병합 포함) 30초면 충분; 초과 시 force kill
                    return await asyncio.wait_for(self.process.wait(), timeout=30.0)
                except TimeoutError:
                    pass
            # 시그널 전달 실패 → 즉시 force kill (기다릴 이유 없음)

        ret = await self._kill_tree()
        self.output_task.cancel()
        return ret

    async def _send_graceful_interrupt(self) -> bool:
        """SIGINT(Ctrl+C)를 자식 프로세스에 전달합니다.

        Windows에서는 CREATE_NEW_CONSOLE로 생성된 자식 프로세스의 콘솔에
        AttachConsole 후 CTRL_C_EVENT(0)를 보냅니다.
        yt-dlp는 SIGINT를 받으면 현재 fragment 수신 완료 후 ffmpeg로 병합하여 정상 종료합니다.
        """
        pid = getattr(self.process, "pid", None)
        if pid is None:
            return False

        if sys.platform != "win32":
            try:
                self.process.send_signal(signal.SIGINT)
                return True
            except ProcessLookupError:
                return False

        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32

            # 부모 프로세스에서 Ctrl+C 핸들러를 일시적으로 비활성화 (부모가 영향받지 않도록)
            kernel32.SetConsoleCtrlHandler(None, True)
            signal_sent = False
            try:
                # 부모의 현재 콘솔에서 분리 (없을 수도 있음 — 무시)
                kernel32.FreeConsole()

                # 자식 프로세스의 콘솔(CREATE_NEW_CONSOLE으로 생성됨)에 연결
                if kernel32.AttachConsole(pid):
                    # CTRL_C_EVENT(0): yt-dlp의 SIGINT 핸들러를 트리거
                    # NOTE: CTRL_BREAK_EVENT(1)는 yt-dlp가 graceful하게 처리하지 않음
                    kernel32.GenerateConsoleCtrlEvent(0, 0)
                    await asyncio.sleep(0.3)
                    kernel32.FreeConsole()
                    signal_sent = True
                # else: AttachConsole 실패 → 시그널 미전달 → signal_sent = False

                # 부모의 콘솔(파이썬 실행 콘솔)에 다시 연결 (최선 노력)
                kernel32.AttachConsole(0xFFFFFFFF)
            finally:
                kernel32.SetConsoleCtrlHandler(None, False)
            return signal_sent
        except Exception:
            pass

        return False

    async def _kill_tree(self) -> int:
        """프로세스 트리 전체를 즉시 kill합니다."""
        import psutil

        try:
            parent = psutil.Process(self.process.pid)
            children = parent.children(recursive=True)
            for child in children:
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
            parent.kill()
        except psutil.NoSuchProcess:
            pass
        except Exception:
            self.process.terminate()

        try:
            return await asyncio.wait_for(self.process.wait(), timeout=5)
        except TimeoutError:
            self.process.kill()
            return await self.process.wait()


class ProcessRunner:
    async def start(self, command: list[str], on_output: OutputCallback) -> RunningProcess:
        """yt-dlp 프로세스를 시작합니다.

        Windows에서는 CREATE_NEW_CONSOLE + SW_HIDE를 사용합니다.
        - CREATE_NEW_CONSOLE: 자식 프로세스에 독립 콘솔을 부여 (AttachConsole 가능하게 함)
        - SW_HIDE: 콘솔 창을 사용자에게 보이지 않게 숨김
        - CREATE_NO_WINDOW는 사용하지 않음: 콘솔 자체가 없으면 CTRL_C_EVENT 전달 불가
        """
        kwargs: dict = {"env": self._subprocess_env()}

        if sys.platform == "win32":
            # CREATE_NEW_CONSOLE: 자식에게 독립 콘솔 부여 (SIGINT 전달에 필수)
            kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
            startupinfo = subprocess.STARTUPINFO()
            # STARTF_USESHOWWINDOW + SW_HIDE(0): 콘솔 창을 숨김
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE
            kwargs["startupinfo"] = startupinfo

        process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            **kwargs,
        )
        output_task = asyncio.create_task(self._pump_output(process, on_output))
        return RunningProcess(command, process, output_task)

    async def _pump_output(
        self,
        process: asyncio.subprocess.Process,
        on_output: OutputCallback,
    ) -> int:
        assert process.stdout is not None
        parser = ProcessOutputParser()

        try:
            while True:
                raw = await process.stdout.read(4096)
                if not raw:
                    break
                for output in parser.feed(raw):
                    await on_output(output)
        except asyncio.CancelledError:
            pass

        tail = parser.finish()
        if tail:
            try:
                await on_output(tail)
            except Exception:
                pass
        return await process.wait()

    def _subprocess_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        return env
