from __future__ import annotations

import locale
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProcessOutput:
    text: str
    replace: bool = False


class ProcessOutputParser:
    def __init__(self) -> None:
        self._buffer = b""
        self._encodings = self._preferred_encodings()

    def feed(self, chunk: bytes) -> list[ProcessOutput]:
        self._buffer += chunk
        outputs: list[ProcessOutput] = []

        while True:
            separator = self._next_separator()
            if separator is None:
                return outputs

            index, length, replace = separator
            raw_line = self._buffer[:index]
            self._buffer = self._buffer[index + length :]
            text = self._decode(raw_line).strip()
            if text:
                outputs.append(ProcessOutput(text=text, replace=replace))

    def finish(self) -> ProcessOutput | None:
        text = self._decode(self._buffer).strip()
        self._buffer = b""
        if not text:
            return None
        return ProcessOutput(text=text)

    def _next_separator(self) -> tuple[int, int, bool] | None:
        cr_index = self._buffer.find(b"\r")
        lf_index = self._buffer.find(b"\n")
        if cr_index == -1 and lf_index == -1:
            return None

        if cr_index != -1 and (lf_index == -1 or cr_index < lf_index):
            if cr_index + 1 < len(self._buffer) and self._buffer[cr_index + 1] == 0x0A:
                return cr_index, 2, False
            return cr_index, 1, True

        return lf_index, 1, False

    def _decode(self, raw: bytes) -> str:
        for encoding in self._encodings:
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace")

    def _preferred_encodings(self) -> tuple[str, ...]:
        candidates = ["utf-8", "cp949", locale.getpreferredencoding(False), "mbcs"]
        deduplicated = []
        for encoding in candidates:
            if encoding and encoding.lower() not in {item.lower() for item in deduplicated}:
                deduplicated.append(encoding)
        return tuple(deduplicated)
