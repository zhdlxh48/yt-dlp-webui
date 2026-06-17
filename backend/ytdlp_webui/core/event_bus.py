from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

from fastapi import WebSocket


class EventBus:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._lock = asyncio.Lock()
        self.recent: list[dict[str, Any]] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._clients.add(websocket)
            recent = list(self.recent[-100:])
        for event in recent:
            await websocket.send_json(event)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(websocket)

    async def publish(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        event = {
            "type": event_type,
            "payload": payload or {},
            "timestamp": datetime.now(UTC).isoformat(),
        }
        async with self._lock:
            self.recent.append(event)
            self.recent = self.recent[-300:]
            clients = list(self._clients)
        stale: list[WebSocket] = []
        for client in clients:
            try:
                await client.send_json(event)
            except RuntimeError:
                stale.append(client)
        if stale:
            async with self._lock:
                for client in stale:
                    self._clients.discard(client)

    async def publish_log(self, message: str, level: str = "info") -> None:
        import logging
        logger = logging.getLogger("ytdlp_webui")
        getattr(logger, level.lower())(message)
        await self.publish(
            "system.log",
            {"line": f"[{datetime.now(UTC).strftime('%H:%M:%S')}] {message}"},
        )


