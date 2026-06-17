from __future__ import annotations

from fastapi import Request

from ytdlp_webui.core.config_store import ConfigStore
from ytdlp_webui.core.event_bus import EventBus
from ytdlp_webui.services.autostart_service import AutostartService
from ytdlp_webui.services.file_service import FileService
from ytdlp_webui.services.recorder_service import RecorderService
from ytdlp_webui.services.tool_service import ToolService


def config_store(request: Request) -> ConfigStore:
    return request.app.state.config_store


def event_bus(request: Request) -> EventBus:
    return request.app.state.event_bus


def tool_service(request: Request) -> ToolService:
    return request.app.state.tool_service


def recorder_service(request: Request) -> RecorderService:
    return request.app.state.recorder_service


def file_service(request: Request) -> FileService:
    return request.app.state.file_service


def autostart_service(request: Request) -> AutostartService:
    return request.app.state.autostart_service

