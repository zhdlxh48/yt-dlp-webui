from __future__ import annotations

import subprocess

from ytdlp_webui.core.paths import exe_path, is_windows

TASK_NAME = "yt-dlp-webui"


class AutostartService:
    def enable(self) -> None:
        if not is_windows():
            return
        subprocess.run(
            [
                "schtasks",
                "/Create",
                "/TN",
                TASK_NAME,
                "/SC",
                "ONLOGON",
                "/TR",
                str(exe_path()),
                "/F",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def disable(self) -> None:
        if not is_windows():
            return
        subprocess.run(
            ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
            check=False,
            capture_output=True,
            text=True,
        )

