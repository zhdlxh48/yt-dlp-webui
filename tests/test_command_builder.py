from __future__ import annotations

from pathlib import Path

from ytdlp_webui.core.paths import AppPaths
from ytdlp_webui.core.schemas import (
    AppConfig,
    LiveChannel,
    PathsConfig,
    Settings,
    ToolInfo,
    ToolStatus,
)
from ytdlp_webui.services.ytdlp_command_builder import YtdlpCommandBuilder


def test_live_command_contains_required_ytdlp_options(tmp_path: Path) -> None:
    paths, settings, tools = make_builder_inputs(tmp_path)
    channel = LiveChannel(
        name="\uba54\ubab0\ud0b4",
        handle="@memolkim",
        url="https://youtube.com/@memolkim/live",
    )

    command = YtdlpCommandBuilder(paths).live(settings, tools, channel)

    assert command[0] == str(paths.tools / "yt-dlp" / "yt-dlp.exe")
    assert "--newline" not in command
    assert "--download-archive" not in command
    assert command[command.index("--encoding") + 1] == "utf-8"
    assert "--wait-for-video" in command
    assert "--live-from-start" in command
    assert "--ffmpeg-location" in command
    assert "--js-runtimes" in command
    assert command[-1] == "https://www.youtube.com/@memolkim/live"

    output_template = command[command.index("--output") + 1]
    assert output_template.startswith("\uba54\ubab0\ud0b4_@memolkim_%(epoch>%Y%m%d_%H%M%S)s/")
    assert "%(epoch>%Y%m%d_%H%M%S)s" in output_template
    assert not any(
        path.name.startswith("\uba54\ubab0\ud0b4_@memolkim_")
        for path in Path(settings.paths.downloads_dir).glob("*")
    )


def test_download_command_keeps_archive(tmp_path: Path) -> None:
    paths, settings, tools = make_builder_inputs(tmp_path)

    command = YtdlpCommandBuilder(paths).download(settings, tools, "https://example.com/video")

    assert command[command.index("--download-archive") + 1] == str(paths.archive_file)


def make_builder_inputs(tmp_path: Path) -> tuple[AppPaths, Settings, ToolStatus]:
    yt_dlp = tmp_path / "tools" / "yt-dlp" / "yt-dlp.exe"
    ffmpeg = tmp_path / "tools" / "ffmpeg" / "ffmpeg.exe"
    deno = tmp_path / "tools" / "deno" / "deno.exe"
    for path in [yt_dlp, ffmpeg, deno]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    downloads_dir = tmp_path / "\ub2e4\uc6b4\ub85c\ub4dc"
    paths = AppPaths(
        app_data=tmp_path,
        logs=tmp_path / "logs",
        tools=tmp_path / "tools",
        settings_file=tmp_path / "settings.toml",
        archive_file=tmp_path / "archive.txt",
        default_downloads=downloads_dir,
    )
    settings = Settings(
        app=AppConfig(),
        paths=PathsConfig(downloads_dir=str(downloads_dir), app_data_dir=str(tmp_path)),
    )
    tools = ToolStatus(
        tools=[
            ToolInfo(name="yt-dlp", installed=True, path=str(yt_dlp)),
            ToolInfo(name="ffmpeg", installed=True, path=str(ffmpeg)),
            ToolInfo(name="deno", installed=True, path=str(deno)),
        ]
    )
    return paths, settings, tools
