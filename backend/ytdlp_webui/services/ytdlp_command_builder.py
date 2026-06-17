from __future__ import annotations

import re
import shlex
from pathlib import Path

from ytdlp_webui.core.paths import AppPaths
from ytdlp_webui.core.schemas import LiveChannel, Settings, ToolStatus


def clean_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name).replace("\ufffd", "").strip()
    return re.sub(r"\s+", " ", cleaned)


class YtdlpCommandBuilder:
    def __init__(self, paths: AppPaths) -> None:
        self.paths = paths

    def live(self, settings: Settings, tools: ToolStatus, channel: LiveChannel) -> list[str]:
        name_part = clean_filename(channel.name)
        handle_part = clean_filename(channel.handle)

        parts = []
        if name_part:
            parts.append(name_part)
        if handle_part:
            parts.append(handle_part)
        parts.append("%(epoch>%Y%m%d_%H%M%S)s")

        folder_template = "_".join(parts)
        custom_output_template = f"{folder_template}/{settings.download.output_template}"

        command = self._base(
            settings,
            tools,
            custom_output_template=custom_output_template,
            use_download_archive=False,
        )
        command.extend(["--wait-for-video", str(settings.live.wait_for_video_seconds)])
        if settings.live.live_from_start:
            command.append("--live-from-start")
        command.append(channel.url)
        return command

    def download(self, settings: Settings, tools: ToolStatus, url: str) -> list[str]:
        command = self._base(settings, tools)
        command.append(url)
        return command

    def _base(
        self,
        settings: Settings,
        tools: ToolStatus,
        custom_output_template: str | None = None,
        use_download_archive: bool = True,
    ) -> list[str]:
        yt_dlp = tools.path_for("yt-dlp") or self._configured_path(settings.tools.yt_dlp_path)
        if yt_dlp is None:
            raise FileNotFoundError("yt-dlp.exe가 설치되어 있지 않습니다.")
        if not yt_dlp.exists():
            raise FileNotFoundError("yt-dlp.exe가 설치되어 있지 않습니다.")

        download = settings.download
        retry = settings.live.retry_policy
        output_template = custom_output_template or download.output_template
        command = [
            str(yt_dlp),
            "--encoding",
            "utf-8",
            "--windows-filenames",
            "--paths",
            settings.paths.downloads_dir,
            "--output",
            output_template,
            "--retries",
            retry.retries,
            "--fragment-retries",
            retry.fragment_retries,
            "--socket-timeout",
            str(retry.socket_timeout),
        ]

        if use_download_archive:
            command.extend(["--download-archive", str(self.paths.archive_file)])

        if download.format_selector:
            command.extend(["--format", download.format_selector])
        if download.merge_output_format:
            command.extend(["--merge-output-format", download.merge_output_format])

        ffmpeg = tools.path_for("ffmpeg") or self._configured_path(settings.tools.ffmpeg_path)
        if ffmpeg and ffmpeg.exists():
            command.extend(["--ffmpeg-location", str(ffmpeg.parent)])

        deno = tools.path_for("deno") or self._configured_path(settings.tools.deno_path)
        if deno and deno.exists():
            command.extend(["--js-runtimes", f"deno:{deno}"])

        cookies = Path(settings.auth.cookies_file) if settings.auth.cookies_file else None
        if cookies and cookies.exists():
            command.extend(["--cookies", str(cookies)])

        if download.extra_args.strip():
            command.extend(shlex.split(download.extra_args, posix=False))

        return command

    def _configured_path(self, value: str) -> Path | None:
        return Path(value) if value.strip() else None
