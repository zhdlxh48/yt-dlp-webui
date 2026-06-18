from __future__ import annotations

from pathlib import Path
from typing import Any

import tomlkit

from ytdlp_webui.core.database import Database
from ytdlp_webui.core.paths import AppPaths
from ytdlp_webui.core.schemas import AppConfig, LiveChannel, PathsConfig, Settings


class ConfigStore:
    def __init__(self, paths: AppPaths) -> None:
        self.paths = paths

    def default_settings(self) -> Settings:
        return Settings(
            app=AppConfig(),
            paths=PathsConfig(
                downloads_dir=str(self.paths.default_downloads),
                app_data_dir=str(self.paths.app_data),
            ),
        )

    def load(self) -> Settings:
        self.paths.ensure()
        db = Database(self.paths.db_file)

        if not self.paths.settings_file.exists():
            settings = self.default_settings()
            self.save(settings)
            return settings

        document = tomlkit.parse(self.paths.settings_file.read_text(encoding="utf-8"))
        data = dict(document)
        
        legacy_channels = data.get("live", {}).get("channels", None)
        settings = Settings.model_validate(self._plain(data))
        settings.paths.app_data_dir = str(self.paths.app_data)

        if legacy_channels is not None:
            channels_list = [LiveChannel.model_validate(c) for c in legacy_channels]
            db.save_channels(channels_list)
            settings.live.channels = channels_list
            self.save(settings)
        else:
            settings.live.channels = db.get_channels()

        return settings

    def save(self, settings: Settings) -> Settings:
        self.paths.ensure()
        normalized = settings.model_copy(deep=True)
        normalized.paths.app_data_dir = str(self.paths.app_data)
        Path(normalized.paths.downloads_dir).mkdir(parents=True, exist_ok=True)
        
        db = Database(self.paths.db_file)
        db.save_channels(normalized.live.channels)

        dump = normalized.model_dump()
        if "live" in dump and "channels" in dump["live"]:
            del dump["live"]["channels"]

        document = tomlkit.document()
        for section, value in dump.items():
            document[section] = value
        self.paths.settings_file.write_text(tomlkit.dumps(document), encoding="utf-8")
        return normalized

    def update(self, payload: dict[str, Any]) -> Settings:
        current = self.load().model_dump()
        merged = self._deep_merge(current, payload)
        return self.save(Settings.model_validate(merged))

    def _plain(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: self._plain(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._plain(item) for item in value]
        return value

    def _deep_merge(self, base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
        result = dict(base)
        for key, value in patch.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

