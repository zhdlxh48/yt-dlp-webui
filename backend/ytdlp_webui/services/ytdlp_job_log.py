from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path

from ytdlp_webui.services.ytdlp_output import YtdlpOutputClassifier


class YtdlpJobLogWriter:
    def __init__(
        self,
        downloads_dir: Path,
        classifier: YtdlpOutputClassifier,
        job_id: str,
        title: str,
    ) -> None:
        self.downloads_dir = downloads_dir
        self.classifier = classifier
        self.job_id = job_id
        self.title = title
        self.path: Path | None = None
        self._prelude: list[str] = []
        self._lock = asyncio.Lock()

    async def write(self, line: str) -> Path | None:
        clean_line = line.strip()
        if not clean_line:
            return None

        async with self._lock:
            opened_path = self._open_when_destination_is_known(clean_line)
            if self.path is None:
                self._prelude.append(clean_line)
                self._prelude = self._prelude[-200:]
                return None

            pending = [*self._prelude, clean_line] if opened_path else [clean_line]
            self._prelude = []
            await asyncio.to_thread(self._append_lines, pending)
            return opened_path

    def _open_when_destination_is_known(self, line: str) -> Path | None:
        if self.path is not None:
            return None

        destination = self.classifier.destination_from_line(line, self.downloads_dir)
        if destination is None:
            return None

        target_dir = destination.parent if destination.suffix else destination
        target_dir.mkdir(parents=True, exist_ok=True)
        self.path = target_dir / "yt-dlp.log"
        return self.path

    def _append_lines(self, lines: list[str]) -> None:
        if self.path is None:
            return

        is_new_file = not self.path.exists() or self.path.stat().st_size == 0
        with self.path.open("a", encoding="utf-8", newline="\n") as file:
            if is_new_file:
                file.write("# yt-dlp-webui log\n")
                file.write(f"# job: {self.job_id}\n")
                file.write(f"# title: {self.title}\n")
                file.write(f"# started: {datetime.now(UTC).isoformat()}\n\n")
            for line in lines:
                file.write(line)
                file.write("\n")
