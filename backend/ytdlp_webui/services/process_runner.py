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
        if self.process.returncode is not None:
            return self.process.returncode

        if not force:
            if self._send_graceful_interrupt():
                return await self.process.wait()

        return await self._kill_tree()

    def _send_graceful_interrupt(self) -> bool:
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
            return self._send_windows_ctrl_c(pid)
        except OSError:
            try:
                self.process.send_signal(signal.CTRL_BREAK_EVENT)
                return True
            except (OSError, ProcessLookupError, ValueError):
                return False

    def _send_windows_ctrl_c(self, pid: int) -> bool:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCtrlHandler(None, True)
        try:
            kernel32.FreeConsole()
            if not kernel32.AttachConsole(pid):
                raise ctypes.WinError()
            if not kernel32.GenerateConsoleCtrlEvent(signal.CTRL_C_EVENT, 0):
                raise ctypes.WinError()
            return True
        finally:
            kernel32.FreeConsole()
            kernel32.SetConsoleCtrlHandler(None, False)

    async def _kill_tree(self) -> int:
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
        kwargs = {"env": self._subprocess_env()}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
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

        while True:
            raw = await process.stdout.read(4096)
            if not raw:
                break
            for output in parser.feed(raw):
                await on_output(output)

        tail = parser.finish()
        if tail:
            await on_output(tail)
        return await process.wait()

    def _subprocess_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        return env
