from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

LineCallback = Callable[[str], Awaitable[None]]


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

    async def stop(self) -> int:
        if self.process.returncode is not None:
            return self.process.returncode
        self.process.terminate()
        try:
            return await asyncio.wait_for(self.process.wait(), timeout=10)
        except TimeoutError:
            self.process.kill()
            return await self.process.wait()


class ProcessRunner:
    async def start(self, command: list[str], on_line: LineCallback) -> RunningProcess:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        output_task = asyncio.create_task(self._pump_output(process, on_line))
        return RunningProcess(command, process, output_task)

    async def _pump_output(
        self,
        process: asyncio.subprocess.Process,
        on_line: LineCallback,
    ) -> int:
        assert process.stdout is not None
        while True:
            raw = await process.stdout.readline()
            if not raw:
                break
            line = raw.decode("utf-8", errors="replace").rstrip()
            if line:
                await on_line(line)
        return await process.wait()

