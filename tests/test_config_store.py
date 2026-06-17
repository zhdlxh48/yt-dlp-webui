from __future__ import annotations

from pathlib import Path

from ytdlp_webui.core.config_store import ConfigStore
from ytdlp_webui.core.paths import AppPaths


def test_config_store_creates_and_updates_toml(tmp_path: Path) -> None:
    paths = AppPaths(
        app_data=tmp_path,
        logs=tmp_path / "logs",
        tools=tmp_path / "tools",
        settings_file=tmp_path / "settings.toml",
        archive_file=tmp_path / "archive.txt",
        default_downloads=tmp_path / "Videos",
    )
    store = ConfigStore(paths)

    settings = store.load()
    assert settings.paths.downloads_dir == str(tmp_path / "Videos")
    assert paths.settings_file.exists()

    updated = store.update({"app": {"open_browser_on_start": False}})
    assert updated.app.open_browser_on_start is False
    assert store.load().app.open_browser_on_start is False

