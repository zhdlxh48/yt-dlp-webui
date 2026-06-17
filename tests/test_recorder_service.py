from __future__ import annotations

import asyncio
from pathlib import Path

from ytdlp_webui.core.config_store import ConfigStore
from ytdlp_webui.core.event_bus import EventBus
from ytdlp_webui.core.paths import AppPaths
from ytdlp_webui.core.schemas import LiveChannel, ToolInfo, ToolStatus
from ytdlp_webui.services.process_output import ProcessOutput
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
    async def start(self, command, on_output):  # noqa: ANN001, ANN201
        await on_output(ProcessOutput("[download] Destination: recording.f299.mp4"))
        await on_output(
            ProcessOutput("[download] 12.3% of 10.00MiB at 1.00MiB/s ETA 00:09", replace=True)
        )
        await on_output(ProcessOutput("regular log line"))
        task = asyncio.create_task(self._finish())
        return FakeRunningProcess(command, task)

    async def _finish(self) -> int:
        await asyncio.sleep(0.01)
        return 0


class FakeRunningProcess:
    def __init__(self, command, output_task):  # noqa: ANN001
        self.command = command
        self.output_task = output_task
        self.pid = 123

    async def stop(self, force: bool = False) -> int:
        return 0


def _paths(tmp_path: Path) -> AppPaths:
    return AppPaths(
        app_data=tmp_path,
        logs=tmp_path / "logs",
        tools=tmp_path / "tools",
        settings_file=tmp_path / "settings.toml",
        archive_file=tmp_path / "archive.txt",
        default_downloads=tmp_path / "Videos",
    )


def test_recorder_starts_live_job(tmp_path: Path) -> None:
    async def run() -> tuple[list, EventBus]:
        yt_dlp = tmp_path / "yt-dlp.exe"
        yt_dlp.write_text("", encoding="utf-8")
        paths = _paths(tmp_path)
        store = ConfigStore(paths)
        settings = store.load()
        settings.tools.yt_dlp_path = str(yt_dlp)
        settings.live.channels = [LiveChannel(name="test", url="https://example.com/live")]
        store.save(settings)
        events = EventBus()
        service = RecorderService(
            config=store,
            tools=FakeTools(yt_dlp),  # type: ignore[arg-type]
            builder=YtdlpCommandBuilder(paths),
            runner=FakeRunner(),  # type: ignore[arg-type]
            events=events,
        )

        jobs = await service.start_live()
        await asyncio.sleep(0.02)
        return jobs, events

    jobs, events = asyncio.run(run())

    assert len(jobs) == 1
    assert jobs[0].status in {"running", "finished"}
    assert not any(event["type"] == "job.progress_line" for event in events.recent)
    assert any(
        event["type"] == "job.log" and "regular log line" in event["payload"]["line"]
        for event in events.recent
    )

    log_file = tmp_path / "Videos" / "yt-dlp.log"
    assert log_file.exists()
    log_text = log_file.read_text(encoding="utf-8")
    assert "[download] Destination: recording.f299.mp4" in log_text
    assert "[download] 12.3%" in log_text
