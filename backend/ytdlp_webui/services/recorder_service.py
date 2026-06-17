from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from ytdlp_webui.core.config_store import ConfigStore
from ytdlp_webui.core.event_bus import EventBus
from ytdlp_webui.core.schemas import JobInfo
from ytdlp_webui.services.process_runner import ProcessRunner, RunningProcess
from ytdlp_webui.services.tool_service import ToolService
from ytdlp_webui.services.ytdlp_command_builder import YtdlpCommandBuilder


class RecorderService:
    def __init__(
        self,
        config: ConfigStore,
        tools: ToolService,
        builder: YtdlpCommandBuilder,
        runner: ProcessRunner,
        events: EventBus,
    ) -> None:
        self.config = config
        self.tools = tools
        self.builder = builder
        self.runner = runner
        self.events = events
        self.jobs: dict[str, JobInfo] = {}
        self.processes: dict[str, RunningProcess] = {}

    async def list_jobs(self) -> list[JobInfo]:
        return list(self.jobs.values())

    async def start_live(self, channel_ids: list[str] | None = None) -> list[JobInfo]:
        await self.events.publish_log("라이브 감시 작업을 시작합니다.")
        settings = self.config.load()
        tool_status = await self.tools.status()
        if not all(t.installed for t in tool_status.tools):
            raise FileNotFoundError(
                "필수 도구(yt-dlp, ffmpeg, deno) 중 일부가 누락되었습니다. "
                "도구 설치를 완료한 후 다시 시도해 주세요."
            )
        selected = [
            channel
            for channel in settings.live.channels
            if channel.enabled and (not channel_ids or channel.id in channel_ids)
        ]
        jobs: list[JobInfo] = []
        for channel in selected:
            title = channel.name or channel.url
            command = self.builder.live(settings, tool_status, channel.url)
            jobs.append(await self._start_job("live", title, command, channel_id=channel.id))
        if not jobs:
            await self.events.publish("app.status", {"message": "감시할 채널이 없습니다."})
            await self.events.publish_log("감시할 채널이 없습니다.", level="warning")
        return jobs

    async def start_download(self, url: str) -> JobInfo:
        await self.events.publish_log(f"일반 다운로드 작업을 시작합니다: {url}")
        settings = self.config.load()
        tool_status = await self.tools.status()
        if not all(t.installed for t in tool_status.tools):
            raise FileNotFoundError(
                "필수 도구(yt-dlp, ffmpeg, deno) 중 일부가 누락되었습니다. "
                "도구 설치를 완료한 후 다시 시도해 주세요."
            )
        command = self.builder.download(settings, tool_status, url)
        return await self._start_job("download", url, command)

    async def stop(self, job_id: str) -> JobInfo:
        job = self.jobs[job_id]
        await self.events.publish_log(f"작업 정지 요청: {job.title} (ID: {job_id})")
        job.status = "stopping"
        await self.events.publish("job.progress", job.model_dump())
        process = self.processes.get(job_id)
        if process:
            code = await process.stop()
            job.return_code = code
            job.status = "stopped"
            job.finished_at = self._now()
            await self.events.publish("job.finished", job.model_dump())
        return job

    async def stop_all(self) -> None:
        for job_id in list(self.processes):
            await self.stop(job_id)

    async def auto_start_if_configured(self) -> None:
        settings = self.config.load()
        if settings.app.start_monitoring_on_launch and settings.live.channels:
            await self.start_live()

    async def _start_job(
        self,
        kind: str,
        title: str,
        command: list[str],
        channel_id: str | None = None,
    ) -> JobInfo:
        job_id = uuid4().hex
        job = JobInfo(
            id=job_id,
            kind=kind,  # type: ignore[arg-type]
            title=title,
            status="starting",
            command=command,
            started_at=self._now(),
            channel_id=channel_id,
        )
        self.jobs[job_id] = job
        await self.events.publish("job.started", job.model_dump())

        async def on_line(line: str) -> None:
            await self.events.publish("job.log", {"job_id": job_id, "line": line})

        process = await self.runner.start(command, on_line)
        self.processes[job_id] = process
        job.status = "running"
        await self.events.publish("job.progress", job.model_dump())
        pid = getattr(process, "pid", None)
        pid_str = f"PID: {pid}" if pid else "PID: N/A"
        await self.events.publish_log(f"작업 프로세스 기동 성공: {title} ({pid_str})")
        asyncio.create_task(self._finish_when_done(job_id, process))
        return job

    async def _finish_when_done(self, job_id: str, process: RunningProcess) -> None:
        code = await process.output_task
        self.processes.pop(job_id, None)
        job = self.jobs[job_id]
        job.return_code = code
        job.finished_at = self._now()
        job.status = "finished" if code == 0 else "failed"
        event = "job.finished" if code == 0 else "job.error"
        await self.events.publish(event, job.model_dump())
        await self.events.publish_log(
            f"작업 종료: {job.title} (종료 코드: {code}, 상태: {job.status})",
            level="info" if code == 0 else "error"
        )

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()

