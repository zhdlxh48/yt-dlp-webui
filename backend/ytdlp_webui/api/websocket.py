from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ytdlp_webui.core.event_bus import EventBus

router = APIRouter()


@router.websocket("/events")
async def websocket_events(websocket: WebSocket) -> None:
    events: EventBus = websocket.app.state.event_bus
    await events.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await events.disconnect(websocket)

