from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from ytdlp_webui.api import files, health, jobs, settings, tools, websocket
from ytdlp_webui.core.config_store import ConfigStore
from ytdlp_webui.core.event_bus import EventBus
from ytdlp_webui.core.logging import configure_logging
from ytdlp_webui.core.paths import AppPaths, frontend_dist_path
from ytdlp_webui.services.autostart_service import AutostartService
from ytdlp_webui.services.file_service import FileService
from ytdlp_webui.services.process_runner import ProcessRunner
from ytdlp_webui.services.recorder_service import RecorderService
from ytdlp_webui.services.tool_service import ToolService
from ytdlp_webui.services.ytdlp_command_builder import YtdlpCommandBuilder


def create_app() -> FastAPI:
    paths = AppPaths.discover()
    paths.ensure()
    configure_logging(paths)
    events = EventBus()
    config = ConfigStore(paths)
    tools_service = ToolService(paths, events)
    recorder = RecorderService(
        config=config,
        tools=tools_service,
        builder=YtdlpCommandBuilder(paths),
        runner=ProcessRunner(),
        events=events,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.paths = paths
        app.state.config_store = config
        app.state.event_bus = events
        app.state.tool_service = tools_service
        app.state.recorder_service = recorder
        app.state.file_service = FileService(config)
        app.state.autostart_service = AutostartService()
        auto_task = asyncio.create_task(recorder.auto_start_if_configured())
        await events.publish("app.status", {"message": "앱이 시작되었습니다."})
        try:
            yield
        finally:
            auto_task.cancel()
            await recorder.stop_all()

    app = FastAPI(title="yt-dlp-webui", version="0.1.0", lifespan=lifespan)
    app.include_router(health.router, prefix="/api")
    app.include_router(settings.router, prefix="/api")
    app.include_router(tools.router, prefix="/api")
    app.include_router(jobs.router, prefix="/api")
    app.include_router(files.router, prefix="/api")
    app.include_router(websocket.router, prefix="/ws")

    dist = frontend_dist_path()
    if dist.exists():
        app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
    else:

        @app.get("/", response_class=HTMLResponse)
        async def missing_frontend() -> str:
            return "<h1>yt-dlp-webui</h1><p>frontend/dist is missing. Run npm run build.</p>"

    return app
