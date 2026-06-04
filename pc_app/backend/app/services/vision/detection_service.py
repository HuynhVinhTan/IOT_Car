from datetime import datetime, timezone
import time
import io
from typing import Any, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool
from app.models.detection import DetectionEvent
from app.repositories.ai_repository import DetectionEventRepository
from app.schemas.mission import DetectionState
from app.navigation.mission_service import MissionService
from app.core.config import settings
from app.services.robot.car_control_service import CarControlService
from app.services.robot.joystick_service import JoystickService
from app.services.media.media_asset_service import MediaAssetService

class DetectionService:
    def __init__(
        self,
        car_control_service: CarControlService,
        joystick_service: JoystickService,
        config_settings: Any = settings,
    ) -> None:
        self._car_control_service = car_control_service
        self._joystick_service = joystick_service
        self._settings = config_settings
        self._mission_service: Optional[MissionService] = None
        self.current_state = DetectionState()

    def set_mission_service(self, mission_service: MissionService):
        self._mission_service = mission_service

    def get_state(self) -> DetectionState:
        return self.current_state

    async def clear_state(self, db: AsyncSession):
        self.current_state = DetectionState(detected_at_ms=int(time.time() * 1000))
        if self._mission_service:
            self._mission_service.detection_state = self.current_state
        
        # Record clear event
        repo = DetectionEventRepository(DetectionEvent, db)
        event = DetectionEvent(
            event_type="CLEAR",
            source="system",
            message="Detection state cleared"
        )
        await repo.create(event)

    async def update_state_custom(self, status: str, message: str):
        self.current_state.status = status
        self.current_state.message = message
        self.current_state.detected_at_ms = int(time.time() * 1000)
        
        if self._mission_service:
            self._mission_service.detection_state = self.current_state
        
        # Hardware signals for critical states
        if status == "CAMERA_NOT_READY":
             await self._try_send_car_command_async({"command": "CAMERA_ERROR"})

    async def update_vision_state(
        self, 
        db: AsyncSession,
        status: str, 
        candidate: Any, 
        face_result: Optional[Any] = None,
        source: str = "camera_pipeline"
    ):
        self.current_state.status = status
        self.current_state.detected_at_ms = int(time.time() * 1000)
        self.current_state.object_found = True
        self.current_state.object_type = "person"
        self.current_state.confidence = candidate.confidence
        self.current_state.last_person_bbox = candidate.bbox
        self.current_state.message = f"Detected: {status}"

        if face_result:
            self.current_state.is_target_found = (status == "TARGET_FOUND")
            self.current_state.last_face_bbox = face_result.bbox
            self.current_state.target_person_id = str(face_result.target_person_id) if face_result.target_person_id else None
            self.current_state.display_name = face_result.display_name

        if self._mission_service:
            self._mission_service.detection_state = self.current_state
            # Map legacy object_found to mission logic
            self._mission_service.trigger_mock_detection(status == "TARGET_FOUND" or status == "PERSON_CANDIDATE")

        # Create Detection Event
        repo = DetectionEventRepository(DetectionEvent, db)
        event = DetectionEvent(
            event_type=status,
            target_person_id=face_result.target_person_id if face_result else None,
            confidence=candidate.confidence,
            source=source,
            person_bbox_json=candidate.bbox,
            face_bbox_json=face_result.bbox if face_result else None,
            message=f"Vision Pipeline: {status}"
        )
        await repo.create(event)

        # Hardware signals
        if status == "TARGET_FOUND":
            await self._try_start_joystick_alert_async()
            if self._settings.stop_on_person_detected:
                await self._try_send_car_command_async({"command": "EMERGENCY_STOP"})
        elif status == "NO_PERSON" or status == "TARGET_LOST":
            await self._try_stop_joystick_alert_async()

    async def person_detected(
        self, 
        db: AsyncSession,
        confidence: float | None = None, 
        source: str = "ai",
        snapshot_file: Optional[Any] = None,
        target_person_id: Optional[Any] = None
    ) -> DetectionEvent:
        # Legacy/Mock support
        snapshot_asset_id = None
        if snapshot_file:
            media_service = MediaAssetService(db)
            asset = await media_service.upload_asset(
                file=snapshot_file,
                folder="detections",
                purpose="detection_snapshot"
            )
            snapshot_asset_id = asset.id

        # Record in DB
        repo = DetectionEventRepository(DetectionEvent, db)
        event = DetectionEvent(
            event_type="PERSON_FOUND",
            target_person_id=target_person_id,
            confidence=confidence,
            source=source,
            snapshot_asset_id=snapshot_asset_id,
            message=f"Person detected via {source}-source"
        )
        event = await repo.create(event)

        # Update State
        self.current_state.status = "TARGET_FOUND" if target_person_id else "PERSON_CANDIDATE"
        self.current_state.object_found = True
        self.current_state.object_type = "person"
        self.current_state.confidence = confidence if confidence is not None else 1.0
        self.current_state.detected_at_ms = int(time.time() * 1000)
        self.current_state.message = f"Person detected ({source})"
        
        if self._mission_service:
            self._mission_service.detection_state = self.current_state
            self._mission_service.trigger_mock_detection(True) 

        # Hardware signals
        await self._try_send_car_command_async({"command": "PERSON_DETECTED", "detected": True})
        if self._settings.enable_joystick_audio_alert:
            await self._try_start_joystick_alert_async()

        if (self._settings.stop_on_person_detected or self._settings.auto_stop_car_on_person_detected):
            await self._try_send_car_command_async({"command": "EMERGENCY_STOP"})

        return event

    async def person_lost(self, db: AsyncSession) -> DetectionEvent:
        repo = DetectionEventRepository(DetectionEvent, db)
        event = DetectionEvent(
            event_type="OBJECT_LOST",
            source="system",
            message="Person lost from view"
        )
        event = await repo.create(event)

        # Update State
        self.current_state.status = "NO_PERSON"
        self.current_state.object_found = False
        self.current_state.message = "Person lost"
        
        if self._mission_service:
            self._mission_service.detection_state = self.current_state
            self._mission_service.trigger_mock_detection(False)

        await self._try_send_car_command_async({"command": "PERSON_LOST"})
        if self._settings.enable_joystick_audio_alert:
            await self._try_stop_joystick_alert_async()
            
        return event

    def _try_send_car_command(self, payload: dict[str, Any]) -> None:
        try:
            self._car_control_service.send_command(payload)
        except Exception:
            pass

    async def _try_send_car_command_async(self, payload: dict[str, Any]) -> None:
        if not self._settings.enable_robot_control:
            return
        await run_in_threadpool(self._try_send_car_command, payload)

    def _try_start_joystick_alert(self) -> None:
        if not self._settings.enable_robot_control:
            return
        try:
            self._joystick_service.start_person_found_alert()
        except Exception:
            pass

    async def _try_start_joystick_alert_async(self) -> None:
        if not self._settings.enable_robot_control:
            return
        await run_in_threadpool(self._try_start_joystick_alert)

    def _try_stop_joystick_alert(self) -> None:
        if not self._settings.enable_robot_control:
            return
        try:
            self._joystick_service.stop_person_found_alert()
        except Exception:
            pass

    async def _try_stop_joystick_alert_async(self) -> None:
        if not self._settings.enable_robot_control:
            return
        await run_in_threadpool(self._try_stop_joystick_alert)
            
    async def get_history(self, db: AsyncSession, limit: int = 50) -> list[DetectionEvent]:
        repo = DetectionEventRepository(DetectionEvent, db)
        return await repo.get_recent(limit)
