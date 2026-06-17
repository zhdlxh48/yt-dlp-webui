from __future__ import annotations

from pathlib import Path

from ytdlp_webui.core.paths import AppPaths
from ytdlp_webui.core.schemas import AppConfig, PathsConfig, Settings, ToolInfo, ToolStatus
from ytdlp_webui.services.ytdlp_command_builder import YtdlpCommandBuilder


def test_live_command_contains_required_ytdlp_options(tmp_path: Path) -> None:
    yt_dlp = tmp_path / "tools" / "yt-dlp" / "yt-dlp.exe"
    ffmpeg = tmp_path / "tools" / "ffmpeg" / "ffmpeg.exe"
    deno = tmp_path / "tools" / "deno" / "deno.exe"
    for path in [yt_dlp, ffmpeg, deno]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    paths = AppPaths(
        app_data=tmp_path,
        logs=tmp_path / "logs",
        tools=tmp_path / "tools",
        settings_file=tmp_path / "settings.toml",
        archive_file=tmp_path / "archive.txt",
        default_downloads=tmp_path / "다운로드",
    )
    settings = Settings(
        app=AppConfig(),
        paths=PathsConfig(downloads_dir=str(tmp_path / "다운로드"), app_data_dir=str(tmp_path)),
    )
    tools = ToolStatus(
        tools=[
            ToolInfo(name="yt-dlp", installed=True, path=str(yt_dlp)),
            ToolInfo(name="ffmpeg", installed=True, path=str(ffmpeg)),
            ToolInfo(name="deno", installed=True, path=str(deno)),
        ]
    )

    command = YtdlpCommandBuilder(paths).live(settings, tools, "https://youtube.com/@memolkim/live")

    assert command[0] == str(yt_dlp)
    assert "--wait-for-video" in command
    assert "--live-from-start" in command
    assert "--ffmpeg-location" in command
    assert "--js-runtimes" in command
    assert command[-1] == "https://youtube.com/@memolkim/live"

