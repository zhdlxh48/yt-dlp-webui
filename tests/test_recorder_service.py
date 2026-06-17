from __future__ import annotations

import asyncio
from pathlib import Path

from ytdlp_webui.core.config_store import ConfigStore
from ytdlp_webui.core.event_bus import EventBus
from ytdlp_webui.core.paths import AppPaths
from ytdlp_webui.core.schemas import LiveChannel, ToolInfo, ToolStatus
from ytdlp_webui.services.recorder_service import RecorderService
from ytdlp_webui.services.ytdlp_command_builder import YtdlpCommandBuilder


class FakeTools:
    def __init__(self, yt_dlp: Path) -> None:
        self.yt_dlp = yt_dlp

    async def install_missing(self) -> ToolStatus:
        return ToolStatus(tools=[ToolInfo(name="yt-dlp", installed=True, path=str(self.yt_dlp))])

    async def status(self) -> ToolStatus:
        return await self.install_missing()


class FakeRunner:
    async def start(self, command, on_line):  # noqa: ANN001, ANN201
        await on_line("started")
        task = asyncio.create_task(self._finish())
        return FakeRunningProcess(command, task)

    async def _finish(self) -> int:
        await asyncio.sleep(0.01)
        return 0


class FakeRunningProcess:
    def __init__(self, command, output_task):  # noqa: ANN001
        self.command = command
        self.output_task = output_task

    async def stop(self) -> int:
        return 0


def test_recorder_starts_live_job(tmp_path: Path) -> None:
    yt_dlp = tmp_path / "yt-dlp.exe"
    yt_dlp.write_text("", encoding="utf-8")
    paths = AppPaths(
        app_data=tmp_path,
        logs=tmp_path / "logs",
        tools=tmp_path / "tools",
        settings_file=tmp_path / "settings.toml",
        archive_file=tmp_path / "archive.txt",
        default_downloads=tmp_path / "Videos",
    )
    store = ConfigStore(paths)
    settings = store.load()
    settings.tools.yt_dlp_path = str(yt_dlp)
    settings.live.channels = [LiveChannel(name="test", url="https://example.com/live")]
    store.save(settings)
    service = RecorderService(
        config=store,
        tools=FakeTools(yt_dlp),  # type: ignore[arg-type]
        builder=YtdlpCommandBuilder(paths),
        runner=FakeRunner(),  # type: ignore[arg-type]
        events=EventBus(),
    )

    jobs = asyncio.run(service.start_live())

    assert len(jobs) == 1
    assert jobs[0].status == "running"
