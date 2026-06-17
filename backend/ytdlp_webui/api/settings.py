from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from ytdlp_webui.api.deps import autostart_service, config_store, event_bus
from ytdlp_webui.core.config_store import ConfigStore
from ytdlp_webui.core.event_bus import EventBus
from ytdlp_webui.core.schemas import Settings
from ytdlp_webui.services.autostart_service import AutostartService

router = APIRouter()
ConfigStoreDep = Annotated[ConfigStore, Depends(config_store)]
EventBusDep = Annotated[EventBus, Depends(event_bus)]
AutostartDep = Annotated[AutostartService, Depends(autostart_service)]


@router.get("/settings", response_model=Settings)
async def get_settings(store: ConfigStoreDep) -> Settings:
    return store.load()


@router.put("/settings", response_model=Settings)
async def put_settings(
    payload: dict[str, Any],
    store: ConfigStoreDep,
    events: EventBusDep,
    autostart: AutostartDep,
) -> Settings:
    settings = store.update(payload)
    if settings.startup.enabled:
        autostart.enable()
    else:
        autostart.disable()
    await events.publish("settings.updated", settings.model_dump())
    await events.publish_log("설정이 업데이트되었습니다.")
    return settings
