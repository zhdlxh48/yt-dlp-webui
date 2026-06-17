from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ytdlp_webui.services.process_output import ProcessOutput

STREAM_PREFIX_PATTERN = re.compile(r"^(?P<stream_id>\d+):\s+")
PERCENT_PROGRESS_PATTERN = re.compile(
    r"^\[download\]\s+(?P<percent>\d+(?:\.\d+)?)%.*?(?:\sat\s+(?P<speed>\S+))?.*?(?:ETA\s+(?P<eta>\S+))?"
)
FRAGMENT_PROGRESS_PATTERN = re.compile(
    r"^\[download\]\s+(?P<size>\S+)\s+at\s+(?P<speed>\S+)\s+\((?P<elapsed>[^)]*)\)"
    r"\s+\(frag\s+(?P<fragment>\d+)/(?P<fragment_total>\d+)\)"
)
DESTINATION_PATTERNS = (
    re.compile(r"^\[download\]\s+Destination:\s+(.+)$"),
    re.compile(r"^\[Merger\]\s+Merging formats into\s+(.+)$"),
    re.compile(r"^\[download\]\s+(.+?)\s+has already been downloaded$"),
)


@dataclass(frozen=True, slots=True)
class DownloadProgress:
    line: str
    stream_id: str = "main"
    percent: float | None = None
    speed: str = ""
    eta: str = ""
    downloaded: str = ""
    elapsed: str = ""
    fragment: int | None = None
    fragment_total: int | None = None


@dataclass(frozen=True, slots=True)
class NormalizedYtdlpLine:
    text: str
    stream_id: str = "main"


class YtdlpOutputClassifier:
    def parse_progress(self, output: ProcessOutput) -> DownloadProgress | None:
        normalized = split_ytdlp_stream(output.text)
        line = normalized.text
        if output.replace and line.startswith("[download]"):
            return self._parse_progress_line(line, normalized.stream_id)
        if self.is_progress_line(line):
            return self._parse_progress_line(line, normalized.stream_id)
        return None

    def is_progress_line(self, line: str) -> bool:
        normalized = normalize_ytdlp_line(line)
        if not normalized.startswith("[download]"):
            return False
        return bool(
            PERCENT_PROGRESS_PATTERN.search(normalized)
            or FRAGMENT_PROGRESS_PATTERN.search(normalized)
        )

    def destination_from_line(self, line: str, downloads_dir: Path) -> Path | None:
        normalized = normalize_ytdlp_line(line)
        for pattern in DESTINATION_PATTERNS:
            match = pattern.match(normalized)
            if not match:
                continue

            destination = match.group(1).strip().strip('"')
            if not destination:
                continue

            output_path = Path(destination)
            if not output_path.is_absolute():
                output_path = downloads_dir / output_path
            return output_path
        return None

    def _parse_progress_line(self, line: str, stream_id: str) -> DownloadProgress:
        percent_match = PERCENT_PROGRESS_PATTERN.search(line)
        if percent_match:
            return DownloadProgress(
                line=line,
                stream_id=stream_id,
                percent=float(percent_match.group("percent")),
                speed=percent_match.group("speed") or "",
                eta=percent_match.group("eta") or "",
            )

        fragment_match = FRAGMENT_PROGRESS_PATTERN.search(line)
        if fragment_match:
            return DownloadProgress(
                line=line,
                stream_id=stream_id,
                speed=fragment_match.group("speed") or "",
                downloaded=fragment_match.group("size") or "",
                elapsed=fragment_match.group("elapsed") or "",
                fragment=int(fragment_match.group("fragment")),
                fragment_total=int(fragment_match.group("fragment_total")),
            )

        return DownloadProgress(line=line, stream_id=stream_id)


def normalize_ytdlp_line(line: str) -> str:
    return split_ytdlp_stream(line).text


def split_ytdlp_stream(line: str) -> NormalizedYtdlpLine:
    stripped = line.strip()
    match = STREAM_PREFIX_PATTERN.match(stripped)
    if not match:
        return NormalizedYtdlpLine(text=stripped)
    return NormalizedYtdlpLine(
        text=stripped[match.end() :],
        stream_id=match.group("stream_id"),
    )
