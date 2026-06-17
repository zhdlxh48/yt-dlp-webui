from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ytdlp_webui.core.config_store import ConfigStore
from ytdlp_webui.core.event_bus import EventBus
from ytdlp_webui.core.schemas import JobInfo, ToolStatus
from ytdlp_webui.services.process_output import ProcessOutput
from ytdlp_webui.services.process_runner import ProcessRunner, RunningProcess
from ytdlp_webui.services.tool_service import ToolService
from ytdlp_webui.services.ytdlp_command_builder import YtdlpCommandBuilder
from ytdlp_webui.services.ytdlp_job_log import YtdlpJobLogWriter
from ytdlp_webui.services.ytdlp_output import DownloadProgress, YtdlpOutputClassifier

PROGRESS_MIN_INTERVAL_SECONDS = 0.4
ACTIVE_STATUSES = {"starting", "running", "stopping"}


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
        self.output_classifier = YtdlpOutputClassifier()
        self.jobs: dict[str, JobInfo] = {}
        self.processes: dict[str, RunningProcess] = {}
        self.stop_tasks: dict[str, asyncio.Task[int]] = {}
        self._progress_last_sent: dict[str, float] = {}

    async def list_jobs(self) -> list[JobInfo]:
        return list(self.jobs.values())

    async def start_live(self, channel_ids: list[str] | None = None) -> list[JobInfo]:
        await self.events.publish_log("라이브 감시 작업을 시작합니다.")
        settings = self.config.load()
        tool_status = await self.tools.status()
        self._ensure_required_tools(tool_status)

        selected_channels = [
            channel
            for channel in settings.live.channels
            if channel.enabled and (not channel_ids or channel.id in channel_ids)
        ]
        jobs: list[JobInfo] = []
        for channel in selected_channels:
            active = self._active_job_for_channel(channel.id)
            if active:
                jobs.append(active)
                continue

            title = channel.name or channel.url
            command = self.builder.live(settings, tool_status, channel)
            jobs.append(await self._start_job("live", title, command, channel_id=channel.id))

        if not jobs:
            await self.events.publish("app.status", {"message": "감시할 채널이 없습니다."})
            await self.events.publish_log("감시할 채널이 없습니다.", level="warning")
        return jobs

    async def start_download(self, url: str) -> JobInfo:
        await self.events.publish_log(f"일반 다운로드 작업을 시작합니다: {url}")
        settings = self.config.load()
        tool_status = await self.tools.status()
        self._ensure_required_tools(tool_status)

        command = self.builder.download(settings, tool_status, url)
        return await self._start_job("download", url, command)

    async def stop(self, job_id: str, force: bool = False, wait: bool = False) -> JobInfo:
        job = self.jobs[job_id]
        await self.events.publish_log(f"작업 정지 요청 (강제: {force}): {job.title} (ID: {job_id})")
        job.status = "stopping"
        await self.events.publish("job.progress", job.model_dump())

        process = self.processes.get(job_id)
        if process is None:
            await self._mark_stopped(job)
            return job

        stop_task = self._request_process_stop(job_id, process, force)
        if wait:
            await stop_task
            await process.output_task
        return job

    async def stop_all(self) -> None:
        await asyncio.gather(
            *(self.stop(job_id, wait=True) for job_id in list(self.processes)),
            return_exceptions=True,
        )

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

        log_writer = self._create_job_log_writer(job_id, title)

        async def on_output(output: ProcessOutput) -> None:
            await self._handle_process_output(job, output, log_writer)

        try:
            process = await self.runner.start(command, on_output)
        except Exception as exc:
            job.status = "failed"
            job.finished_at = self._now()
            await self.events.publish("job.error", job.model_dump())
            await self.events.publish_log(
                f"작업 프로세스 기동 실패: {title} ({exc})",
                level="error",
            )
            raise

        self.processes[job_id] = process
        job.status = "running"
        await self.events.publish("job.progress", job.model_dump())
        pid = process.pid or "N/A"
        await self.events.publish_log(f"작업 프로세스 기동 성공: {title} (PID: {pid})")
        asyncio.create_task(self._finish_when_done(job_id, process))
        return job

    async def _handle_process_output(
        self,
        job: JobInfo,
        output: ProcessOutput,
        log_writer: YtdlpJobLogWriter,
    ) -> None:
        line = output.text.strip()
        if not line:
            return

        log_path = await log_writer.write(line)
        if log_path is not None:
            await self.events.publish(
                "job.log",
                {"job_id": job.id, "line": f"yt-dlp 상세 로그 저장: {log_path}"},
            )

        progress = self.output_classifier.parse_progress(output)
        if progress is not None:
            await self._publish_progress_line(job.id, job.title, progress)
            return

        await self.events.publish("job.log", {"job_id": job.id, "line": line})

    async def _finish_when_done(self, job_id: str, process: RunningProcess) -> None:
        code = await process.output_task
        self.processes.pop(job_id, None)
        self.stop_tasks.pop(job_id, None)
        self._forget_job_progress(job_id)

        job = self.jobs[job_id]
        was_stopping = job.status == "stopping"
        if was_stopping:
            job.status = "stopped"
        elif job.status != "stopped":
            job.status = "finished" if code == 0 else "failed"

        job.return_code = code
        job.finished_at = self._now()
        await self.events.publish(
            "job.finished" if code == 0 or job.status == "stopped" else "job.error",
            job.model_dump(),
        )
        await self.events.publish_log(
            f"작업 종료: {job.title} (종료 코드: {code}, 상태: {job.status})",
            level="info" if code == 0 or job.status == "stopped" else "error",
        )

        if job.kind == "live" and job.channel_id and not was_stopping:
            asyncio.create_task(self._restart_live_after_delay(job.channel_id))

    async def _restart_live_after_delay(self, channel_id: str) -> None:
        await asyncio.sleep(10)
        settings = self.config.load()
        channel = next((item for item in settings.live.channels if item.id == channel_id), None)
        if channel and channel.enabled and self._active_job_for_channel(channel_id) is None:
            await self.events.publish_log(
                f"라이브 채널 감시를 재시작합니다: {channel.name or channel.url}"
            )
            await self.start_live([channel_id])

    async def _mark_stopped(self, job: JobInfo) -> None:
        job.status = "stopped"
        job.finished_at = self._now()
        await self.events.publish("job.finished", job.model_dump())

    async def _publish_progress_line(
        self,
        job_id: str,
        title: str,
        progress: DownloadProgress,
    ) -> None:
        loop_time = asyncio.get_running_loop().time()
        progress_key = f"{job_id}:{progress.stream_id}"
        last_sent = self._progress_last_sent.get(progress_key, 0)
        if progress.percent != 100 and loop_time - last_sent < PROGRESS_MIN_INTERVAL_SECONDS:
            return

        self._progress_last_sent[progress_key] = loop_time
        await self.events.publish(
            "job.progress_line",
            {
                "job_id": job_id,
                "stream_id": progress.stream_id,
                "title": title,
                "line": progress.line,
                "percent": progress.percent,
                "speed": progress.speed,
                "eta": progress.eta,
                "downloaded": progress.downloaded,
                "elapsed": progress.elapsed,
                "fragment": progress.fragment,
                "fragment_total": progress.fragment_total,
            },
            retain=False,
        )

    def _request_process_stop(
        self,
        job_id: str,
        process: RunningProcess,
        force: bool,
    ) -> asyncio.Task[int]:
        if not force and job_id in self.stop_tasks:
            return self.stop_tasks[job_id]

        task = asyncio.create_task(process.stop(force=force))
        self.stop_tasks[job_id] = task
        task.add_done_callback(lambda _: self.stop_tasks.pop(job_id, None))
        return task

    def _forget_job_progress(self, job_id: str) -> None:
        prefix = f"{job_id}:"
        self._progress_last_sent = {
            key: value
            for key, value in self._progress_last_sent.items()
            if not key.startswith(prefix)
        }

    def _create_job_log_writer(self, job_id: str, title: str) -> YtdlpJobLogWriter:
        downloads_dir = Path(self.config.load().paths.downloads_dir)
        return YtdlpJobLogWriter(downloads_dir, self.output_classifier, job_id, title)

    def _active_job_for_channel(self, channel_id: str) -> JobInfo | None:
        return next(
            (
                job
                for job in self.jobs.values()
                if job.channel_id == channel_id and job.status in ACTIVE_STATUSES
            ),
            None,
        )

    def _ensure_required_tools(self, tool_status: ToolStatus) -> None:
        if all(tool.installed for tool in tool_status.tools):
            return
        raise FileNotFoundError(
            "필수 도구(yt-dlp, ffmpeg, deno) 중 일부가 누락되었습니다. "
            "도구 설치를 완료한 후 다시 시도해 주세요."
        )

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()
