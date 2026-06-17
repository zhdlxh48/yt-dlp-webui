from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler

from ytdlp_webui.core.paths import AppPaths


def configure_logging(paths: AppPaths) -> None:
    paths.ensure()
    log_file = paths.logs / "app.log"
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler = RotatingFileHandler(log_file, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)
    if sys.stderr:
        root.addHandler(logging.StreamHandler())
