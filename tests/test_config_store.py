from __future__ import annotations

from pathlib import Path

import tomlkit
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


def test_config_store_migrates_legacy_toml_channels(tmp_path: Path) -> None:
    paths = AppPaths(
        app_data=tmp_path,
        logs=tmp_path / "logs",
        tools=tmp_path / "tools",
        settings_file=tmp_path / "settings.toml",
        archive_file=tmp_path / "archive.txt",
        default_downloads=tmp_path / "Videos",
    )

    # 1. Create a legacy settings.toml with channels
    document = tomlkit.document()
    document["app"] = {"open_browser_on_start": True}
    document["paths"] = {"downloads_dir": str(tmp_path / "Videos")}
    document["live"] = {
        "channels": [
            {
                "id": "chan1",
                "name": "Legacy Channel 1",
                "handle": "@legacy1",
                "url": "https://www.youtube.com/@legacy1/live",
                "enabled": True,
            }
        ]
    }
    paths.settings_file.write_text(tomlkit.dumps(document), encoding="utf-8")

    # 2. Load config store
    store = ConfigStore(paths)
    settings = store.load()

    # Verify migration loaded channels correctly
    assert len(settings.live.channels) == 1
    assert settings.live.channels[0].id == "chan1"
    assert settings.live.channels[0].name == "Legacy Channel 1"

    # Verify channels were saved to SQLite
    from ytdlp_webui.core.database import Database

    db = Database(paths.db_file)
    db_channels = db.get_channels()
    assert len(db_channels) == 1
    assert db_channels[0].id == "chan1"

    # Verify channels were removed from settings.toml
    saved_toml = tomlkit.parse(paths.settings_file.read_text(encoding="utf-8"))
    assert "channels" not in saved_toml.get("live", {})


