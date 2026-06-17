from __future__ import annotations

import logging
import subprocess

from ytdlp_webui.core.paths import exe_path, is_windows

TASK_NAME = "yt-dlp-webui"
logger = logging.getLogger("ytdlp_webui")


class AutostartService:
    def enable(self) -> None:
        if not is_windows():
            return
        try:
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
                stdin=subprocess.DEVNULL,
            )
        except (OSError, subprocess.SubprocessError) as e:
            logger.error(f"Failed to enable autostart task: {e}")

    def disable(self) -> None:
        if not is_windows():
            return
        try:
            subprocess.run(
                ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
                check=False,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
            )
        except (OSError, subprocess.SubprocessError) as e:
            logger.error(f"Failed to disable autostart task: {e}")


