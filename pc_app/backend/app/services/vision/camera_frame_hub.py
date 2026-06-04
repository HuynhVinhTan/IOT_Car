import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from fastapi import WebSocket


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CameraStreamState:
    camera_id: str
    publisher: WebSocket | None = None
    viewers: set[WebSocket] = field(default_factory=set)
    latest_frame_bytes: bytes | None = None
    status: str = "CAMERA_PUBLISHER_OFFLINE"
    last_frame_at: str | None = None
    last_seen_at: str | None = None
    last_frame_monotonic: float | None = None
    last_error: str | None = None
    frame_count: int = 0
    fps_estimate: float = 0.0
    last_frame_size: int = 0
    accepted_frame_monotonic: float = 0.0
    dropped_frames: int = 0
    last_drop_reason: str | None = None


class CameraFrameHub:
    def __init__(
        self,
        *,
        max_frame_bytes: int,
        max_fps: float,
        offline_timeout_seconds: float,
        max_viewers_per_camera: int,
        viewer_send_timeout_seconds: float,
    ) -> None:
        self._states: dict[str, CameraStreamState] = {}
        self._max_frame_bytes = max_frame_bytes
        self._min_frame_interval = 1.0 / max_fps if max_fps > 0 else 0.0
        self._offline_timeout_seconds = offline_timeout_seconds
        self._max_viewers_per_camera = max_viewers_per_camera
        self._viewer_send_timeout_seconds = viewer_send_timeout_seconds

    async def register_publisher(self, camera_id: str, websocket: WebSocket) -> None:
        state = self._get_state(camera_id)
        if state.publisher is not None and state.publisher is not websocket:
            try:
                await state.publisher.close(code=4000, reason="publisher replaced")
            except RuntimeError:
                pass

        state.publisher = websocket
        state.status = "CAMERA_NOT_READY"
        state.last_seen_at = _utc_now_iso()
        state.last_error = None

    async def unregister_publisher(self, camera_id: str, websocket: WebSocket) -> None:
        state = self._get_state(camera_id)
        if state.publisher is websocket:
            state.publisher = None
            state.status = "CAMERA_PUBLISHER_OFFLINE"
            state.last_seen_at = _utc_now_iso()
            await self.broadcast_status(camera_id, "Camera publisher disconnected")

    async def register_viewer(self, camera_id: str, websocket: WebSocket) -> bool:
        state = self._get_state(camera_id)
        if len(state.viewers) >= self._max_viewers_per_camera:
            return False

        state.viewers.add(websocket)
        await websocket.send_json(self.get_status(camera_id, message_type="camera_status"))
        if state.latest_frame_bytes:
            await websocket.send_bytes(state.latest_frame_bytes)
        return True

    def unregister_viewer(self, camera_id: str, websocket: WebSocket) -> None:
        state = self._get_state(camera_id)
        state.viewers.discard(websocket)

    async def handle_frame(self, camera_id: str, frame_bytes: bytes) -> dict[str, Any]:
        state = self._get_state(camera_id)
        now_monotonic = time.monotonic()
        state.last_seen_at = _utc_now_iso()

        validation_error = self._validate_frame(frame_bytes)
        if validation_error:
            state.last_error = validation_error
            state.status = "CAMERA_NOT_READY"
            state.dropped_frames += 1
            state.last_drop_reason = validation_error
            return {"accepted": False, "reason": validation_error}

        if (
            self._min_frame_interval > 0
            and now_monotonic - state.accepted_frame_monotonic < self._min_frame_interval
        ):
            state.dropped_frames += 1
            state.last_drop_reason = "FRAME_RATE_LIMITED"
            return {"accepted": False, "reason": "FRAME_RATE_LIMITED"}

        if state.last_frame_monotonic is not None:
            elapsed = max(now_monotonic - state.last_frame_monotonic, 0.001)
            instant_fps = 1.0 / elapsed
            state.fps_estimate = (
                instant_fps
                if state.fps_estimate == 0.0
                else (state.fps_estimate * 0.8) + (instant_fps * 0.2)
            )

        state.accepted_frame_monotonic = now_monotonic
        state.last_frame_monotonic = now_monotonic
        state.latest_frame_bytes = frame_bytes
        state.last_frame_at = _utc_now_iso()
        state.last_frame_size = len(frame_bytes)
        state.frame_count += 1
        state.last_error = None
        state.status = "READY"
        state.last_drop_reason = None

        await self._broadcast_frame(state, frame_bytes)
        return {"accepted": True}

    async def handle_heartbeat(self, camera_id: str) -> None:
        state = self._get_state(camera_id)
        state.last_seen_at = _utc_now_iso()
        if state.status == "CAMERA_PUBLISHER_OFFLINE":
            state.status = "CAMERA_NOT_READY"

    async def broadcast_status(self, camera_id: str, message: str = "") -> None:
        state = self._get_state(camera_id)
        payload = self.get_status(camera_id, message_type="camera_status")
        if message:
            payload["message"] = message

        disconnected: list[WebSocket] = []
        for viewer in list(state.viewers):
            try:
                await viewer.send_json(payload)
            except RuntimeError:
                disconnected.append(viewer)

        for viewer in disconnected:
            state.viewers.discard(viewer)

    def get_latest_frame(self, camera_id: str) -> bytes | None:
        return self._get_state(camera_id).latest_frame_bytes

    def get_status(self, camera_id: str, message_type: str | None = None) -> dict[str, Any]:
        state = self._get_state(camera_id)
        self._refresh_offline_status(state)
        payload = {
            "camera_id": camera_id,
            "status": state.status,
            "publisher_connected": state.publisher is not None,
            "viewer_count": len(state.viewers),
            "last_frame_at": state.last_frame_at,
            "last_seen_at": state.last_seen_at,
            "last_frame_size": state.last_frame_size,
            "frame_count": state.frame_count,
            "fps_estimate": round(state.fps_estimate, 2),
            "dropped_frames": state.dropped_frames,
            "last_drop_reason": state.last_drop_reason,
            "last_error": state.last_error,
        }
        if message_type is not None:
            payload["type"] = message_type
        return payload

    async def _broadcast_frame(self, state: CameraStreamState, frame_bytes: bytes) -> None:
        disconnected: list[WebSocket] = []
        for viewer in list(state.viewers):
            try:
                await asyncio.wait_for(
                    viewer.send_bytes(frame_bytes),
                    timeout=self._viewer_send_timeout_seconds,
                )
            except (RuntimeError, TimeoutError, asyncio.TimeoutError):
                disconnected.append(viewer)

        for viewer in disconnected:
            state.viewers.discard(viewer)

    def _get_state(self, camera_id: str) -> CameraStreamState:
        if camera_id not in self._states:
            self._states[camera_id] = CameraStreamState(camera_id=camera_id)
        return self._states[camera_id]

    def _refresh_offline_status(self, state: CameraStreamState) -> None:
        if state.publisher is None:
            state.status = "CAMERA_PUBLISHER_OFFLINE"
            return

        if state.last_frame_monotonic is None:
            state.status = "CAMERA_NOT_READY"
            return

        if time.monotonic() - state.last_frame_monotonic > self._offline_timeout_seconds:
            state.status = "CAMERA_PUBLISHER_OFFLINE"

    def _validate_frame(self, frame_bytes: bytes) -> str | None:
        if not frame_bytes:
            return "EMPTY_FRAME"
        if len(frame_bytes) > self._max_frame_bytes:
            return "FRAME_TOO_LARGE"
        if len(frame_bytes) < 4 or not (
            frame_bytes.startswith(b"\xff\xd8") and frame_bytes.endswith(b"\xff\xd9")
        ):
            return "INVALID_JPEG"
        return None
