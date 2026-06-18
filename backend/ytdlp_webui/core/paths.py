from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from platformdirs import PlatformDirs

APP_NAME = "yt-dlp-webui"


@dataclass(frozen=True)
class AppPaths:
    app_data: Path
    logs: Path
    tools: Path
    settings_file: Path
    archive_file: Path
    default_downloads: Path
    db_file: Path = Path()

    def __post_init__(self) -> None:
        if self.db_file == Path():
            object.__setattr__(self, "db_file", self.app_data / "webui.db")

    @classmethod
    def discover(cls) -> AppPaths:
        dirs = PlatformDirs(APP_NAME, appauthor=False, roaming=True)
        app_data = Path(dirs.user_data_dir)
        default_downloads = Path.home() / "Videos" / APP_NAME
        return cls(
            app_data=app_data,
            logs=app_data / "logs",
            tools=app_data / "tools",
            settings_file=app_data / "settings.toml",
            archive_file=app_data / "archive.txt",
            db_file=app_data / "webui.db",
            default_downloads=default_downloads,
        )

    def ensure(self) -> None:
        for path in [
            self.app_data,
            self.logs,
            self.tools,
            self.tools / "yt-dlp",
            self.tools / "ffmpeg",
            self.tools / "deno",
            self.default_downloads,
        ]:
            path.mkdir(parents=True, exist_ok=True)
        self.archive_file.touch(exist_ok=True)


def resource_path(*parts: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path.cwd()))
    return base.joinpath(*parts)


def frontend_dist_path() -> Path:
    bundled = resource_path("frontend_dist")
    if bundled.exists():
        return bundled
    return Path(__file__).resolve().parents[3] / "frontend" / "dist"


def exe_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable)
    return Path(sys.argv[0]).resolve()


def is_windows() -> bool:
    return os.name == "nt"
