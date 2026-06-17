from __future__ import annotations

import shlex
from pathlib import Path

from ytdlp_webui.core.paths import AppPaths
from ytdlp_webui.core.schemas import Settings, ToolStatus


class YtdlpCommandBuilder:
    def __init__(self, paths: AppPaths) -> None:
        self.paths = paths

    def live(self, settings: Settings, tools: ToolStatus, url: str) -> list[str]:
        command = self._base(settings, tools)
        command.extend(["--wait-for-video", str(settings.live.wait_for_video_seconds)])
        if settings.live.live_from_start:
            command.append("--live-from-start")
        command.append(url)
        return command

    def download(self, settings: Settings, tools: ToolStatus, url: str) -> list[str]:
        command = self._base(settings, tools)
        command.append(url)
        return command

    def _base(self, settings: Settings, tools: ToolStatus) -> list[str]:
        yt_dlp = tools.path_for("yt-dlp") or Path(settings.tools.yt_dlp_path)
        if not yt_dlp.exists():
            raise FileNotFoundError("yt-dlp.exe가 설치되어 있지 않습니다.")

        download = settings.download
        retry = settings.live.retry_policy
        command = [
            str(yt_dlp),
            "--newline",
            "--windows-filenames",
            "--paths",
            settings.paths.downloads_dir,
            "--output",
            download.output_template,
            "--download-archive",
            str(self.paths.archive_file),
            "--retries",
            retry.retries,
            "--fragment-retries",
            retry.fragment_retries,
            "--socket-timeout",
            str(retry.socket_timeout),
        ]
        if download.format_selector:
            command.extend(["--format", download.format_selector])
        if download.merge_output_format:
            command.extend(["--merge-output-format", download.merge_output_format])

        ffmpeg = tools.path_for("ffmpeg") or Path(settings.tools.ffmpeg_path)
        if ffmpeg.exists():
            command.extend(["--ffmpeg-location", str(ffmpeg.parent)])

        deno = tools.path_for("deno") or Path(settings.tools.deno_path)
        if deno.exists():
            command.extend(["--js-runtimes", f"deno:{deno}"])

        cookies = Path(settings.auth.cookies_file) if settings.auth.cookies_file else None
        if cookies and cookies.exists():
            command.extend(["--cookies", str(cookies)])

        if download.extra_args.strip():
            command.extend(shlex.split(download.extra_args, posix=False))

        return command

