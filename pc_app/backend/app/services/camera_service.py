import os
import time
from datetime import datetime, timezone
from typing import Any, Optional

from starlette.concurrency import run_in_threadpool

from app.core.config import Settings


class CameraService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.latest_camera_status: dict[str, Any] = {
            "status": "NOT_CONFIGURED",
            "configured": bool(self._settings.esp32_cam_stream_url),
            "connected": False,
            "source": self._settings.esp32_cam_stream_url,
            "last_checked_at": None,
            "last_error": None,
            "message": "Camera service initialized",
        }

    def get_status(self) -> dict[str, Any]:
        self.latest_camera_status["configured"] = bool(self._settings.esp32_cam_stream_url)
        self.latest_camera_status["source"] = self._settings.esp32_cam_stream_url
        if not self._settings.esp32_cam_stream_url:
            self._set_status(
                status="NOT_CONFIGURED",
                connected=False,
                message="No ESP32_CAM_STREAM_URL configured",
            )
            return self.latest_camera_status

        if self.latest_camera_status.get("status") == "NOT_CONFIGURED":
            self.latest_camera_status.update(
                {
                    "status": "CAMERA_NOT_READY",
                    "connected": False,
                    "message": "Camera stream URL is configured but has not been verified",
                }
            )

        return self.latest_camera_status

    async def check_connection(self) -> dict[str, Any]:
        await run_in_threadpool(self._capture_frame_bytes_sync)
        return self.get_status()

    async def capture_frame_bytes(self) -> Optional[bytes]:
        return await run_in_threadpool(self._capture_frame_bytes_sync)

    async def capture_frame(self, target_dir: str) -> Optional[str]:
        return await run_in_threadpool(self._capture_frame_to_file_sync, target_dir)

    def _capture_frame_bytes_sync(self) -> Optional[bytes]:
        url = self._settings.esp32_cam_stream_url
        if not url:
            self._set_status(
                status="NOT_CONFIGURED",
                connected=False,
                message="No ESP32_CAM_STREAM_URL configured",
            )
            return None

        try:
            import cv2
        except ImportError as exc:
            self._set_status(
                status="CAMERA_NOT_READY",
                connected=False,
                message="OpenCV is not installed",
                error=str(exc),
            )
            return None

        cap = cv2.VideoCapture(url)
        try:
            if not cap.isOpened():
                self._set_status(
                    status="CAMERA_NOT_READY",
                    connected=False,
                    message="Unable to open ESP32-CAM stream",
                    error=f"Failed to open stream: {url}",
                )
                return None

            ret, frame = cap.read()
            if not ret or frame is None:
                self._set_status(
                    status="CAMERA_NOT_READY",
                    connected=False,
                    message="Unable to read frame from ESP32-CAM stream",
                    error=f"Frame read failed: {url}",
                )
                return None

            ok, buffer = cv2.imencode(".jpg", frame)
            if not ok:
                self._set_status(
                    status="CAMERA_NOT_READY",
                    connected=False,
                    message="Unable to encode camera frame",
                    error="cv2.imencode failed",
                )
                return None

            self._set_status(
                status="READY",
                connected=True,
                message="Camera frame captured",
            )
            return buffer.tobytes()
        finally:
            cap.release()

    def _capture_frame_to_file_sync(self, target_dir: str) -> Optional[str]:
        url = self._settings.esp32_cam_stream_url
        if not url:
            self._set_status(
                status="NOT_CONFIGURED",
                connected=False,
                message="No ESP32_CAM_STREAM_URL configured",
            )
            return None

        try:
            import cv2
        except ImportError as exc:
            self._set_status(
                status="CAMERA_NOT_READY",
                connected=False,
                message="OpenCV is not installed",
                error=str(exc),
            )
            return None

        cap = cv2.VideoCapture(url)
        try:
            if not cap.isOpened():
                self._set_status(
                    status="CAMERA_NOT_READY",
                    connected=False,
                    message="Unable to open ESP32-CAM stream",
                    error=f"Failed to open stream: {url}",
                )
                return None

            ret, frame = cap.read()
            if not ret or frame is None:
                self._set_status(
                    status="CAMERA_NOT_READY",
                    connected=False,
                    message="Unable to read frame from ESP32-CAM stream",
                    error=f"Frame read failed: {url}",
                )
                return None

            frame_filename = f"frame_{int(time.time() * 1000)}.jpg"
            target_path = os.path.join(target_dir, frame_filename)
            os.makedirs(target_dir, exist_ok=True)

            if not cv2.imwrite(target_path, frame):
                self._set_status(
                    status="CAMERA_NOT_READY",
                    connected=False,
                    message="Unable to save camera frame",
                    error=f"cv2.imwrite failed: {target_path}",
                )
                return None

            self._set_status(
                status="READY",
                connected=True,
                message="Camera frame saved",
            )
            return os.path.join("frames", frame_filename)
        finally:
            cap.release()

    def _set_status(
        self,
        *,
        status: str,
        connected: bool,
        message: str,
        error: Optional[str] = None,
    ) -> None:
        self.latest_camera_status.update(
            {
                "status": status,
                "configured": bool(self._settings.esp32_cam_stream_url),
                "connected": connected,
                "source": self._settings.esp32_cam_stream_url,
                "last_checked_at": datetime.now(timezone.utc).isoformat(),
                "last_error": error,
                "message": message,
            }
        )
