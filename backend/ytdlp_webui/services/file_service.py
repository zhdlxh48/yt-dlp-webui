from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from ytdlp_webui.core.config_store import ConfigStore
from ytdlp_webui.core.schemas import FileInfo


class FileService:
    def __init__(self, config: ConfigStore) -> None:
        self.config = config

    def list_files(self) -> list[FileInfo]:
        settings = self.config.load()
        root = Path(settings.paths.downloads_dir)
        if not root.exists():
            return []
        files: list[FileInfo] = []
        for path in root.iterdir():
            if not path.is_file():
                continue
            stat = path.stat()
            files.append(
                FileInfo(
                    name=path.name,
                    path=str(path),
                    size=stat.st_size,
                    modified_at=datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
                )
            )
        return sorted(files, key=lambda item: item.modified_at, reverse=True)

