import time
import io
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.training import TrainingSample, TrainingSession
from app.repositories.training_repository import TrainingSampleRepository
from app.services.ai.training_session_service import TrainingSessionService
from app.services.robot.telemetry_service import TelemetryService
from app.services.robot.joystick_service import JoystickService
from app.services.camera.camera_service import CameraService
from app.services.media.media_asset_service import MediaAssetService

class TrainingSampleService:
    def __init__(
        self, 
        db: AsyncSession,
        session_service: TrainingSessionService,
        telemetry_service: TelemetryService,
        joystick_service: JoystickService,
        camera_service: CameraService
    ):
        self.db = db
        self.session_service = session_service
        self.telemetry_service = telemetry_service
        self.joystick_service = joystick_service
        self.camera_service = camera_service
        self.repo = TrainingSampleRepository(TrainingSample, db)
        self.media_service = MediaAssetService(db)

    async def record_sample(self, notes: Optional[str] = None) -> Optional[TrainingSample]:
        session: TrainingSession = await self.session_service.get_current_session()
        if not session or session.status != "RECORDING":
            return None

        # Capture frame if requested
        media_asset_id = None
        if session.record_camera:
            frame_bytes = await self.camera_service.capture_frame_bytes()
            if frame_bytes:
                file_obj = io.BytesIO(frame_bytes)
                file_obj.name = f"frame_{int(time.time()*1000)}.jpg"
                asset = await self.media_service.upload_asset(
                    file=file_obj,
                    folder=f"training/{session.id}",
                    purpose="training_frame",
                    filename=file_obj.name
                )
                media_asset_id = asset.id

        # Gather data
        telemetry = self.telemetry_service.get_latest_telemetry() or {}
        joystick = self.joystick_service.get_latest_telemetry() or {}
        
        timestamp_ms = int(time.time() * 1000)
        
        sample = TrainingSample(
            session_id=session.id,
            media_asset_id=media_asset_id,
            timestamp_ms=timestamp_ms,
            segment_id=session.segment_id,
            direction=session.direction,
            current_node=session.start_node, 
            target_node=session.target_node,
            joystick_x=int(joystick.get("x", 0)),
            joystick_y=int(joystick.get("y", 0)),
            left_motor_speed=telemetry.get("left_motor_speed", 0),
            right_motor_speed=telemetry.get("right_motor_speed", 0),
            front_distance_cm=telemetry.get("front_distance_cm"),
            left_distance_cm=telemetry.get("left_distance_cm"),
            right_distance_cm=telemetry.get("right_distance_cm"),
            rear_distance_cm=telemetry.get("rear_distance_cm"),
            forward_unsafe=telemetry.get("forward_unsafe", False),
            object_found=telemetry.get("person_detected", False),
            notes=notes
        )

        sample = await self.repo.create(sample)

        # Update count in session
        samples = await self.repo.get_by_session(session.id)
        await self.session_service.update_sample_count(session.id, len(samples))
        
        return sample
