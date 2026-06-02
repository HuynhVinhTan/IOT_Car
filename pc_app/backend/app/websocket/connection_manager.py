from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._active_connections:
            self._active_connections.remove(websocket)

    async def broadcast_json(self, payload: dict[str, Any]) -> None:
        for websocket in list(self._active_connections):
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                self.disconnect(websocket)
