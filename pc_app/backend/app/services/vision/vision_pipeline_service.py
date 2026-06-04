from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.schemas.vision import VisionAnalysisResult
from app.services.vision.detection_service import DetectionService
from app.services.face.face_recognition_service import FaceRecognitionService
from app.services.vision.person_detection_service import PersonDetectionService
from app.services.robot.robot_decision_service import RobotDecisionService

class VisionPipelineService:
    def __init__(
        self,
        person_service: PersonDetectionService,
        face_service: FaceRecognitionService,
        detection_service: DetectionService,
        robot_decision_service: RobotDecisionService
    ):
        self.person_service = person_service
        self.face_service = face_service
        self.detection_service = detection_service
        self.robot_decision_service = robot_decision_service
        self.last_yolo_time = 0
        self.yolo_interval = 0.5 # seconds

    async def analyze_frame(
        self, 
        db: AsyncSession,
        image_path: Optional[str] = None, 
        image_bytes: Optional[bytes] = None,
        source: str = "camera"
    ) -> VisionAnalysisResult:
        import time
        
        # 1. Person Detection (Throttled)
        current_time = time.time()
        if current_time - self.last_yolo_time < self.yolo_interval:
            person_result = PersonDetectionResult(status="SKIPPED", candidates=[], provider="YOLOv8n")
        else:
            person_result = await self.person_service.detect_persons(image_path=image_path, image_bytes=image_bytes)
            self.last_yolo_time = current_time
        
        # If provider not ready
        if person_result.status == "PROVIDER_NOT_READY":
            await self.detection_service.update_state_custom(
                status="PROVIDER_NOT_READY",
                message=person_result.message or "Person detector not ready"
            )
            return VisionAnalysisResult(
                status="PROVIDER_NOT_READY",
                detection_state=self.detection_service.get_state().dict(),
                message=person_result.message
            )

        # 2. Handle Candidates
        if not person_result.candidates:
            await self.detection_service.update_state_custom(
                status="NO_PERSON",
                message="No persons in frame"
            )
            result = VisionAnalysisResult(
                status="NO_PERSON",
                detection_state=self.detection_service.get_state().dict()
            )
            await self.robot_decision_service.process_vision_result(result)
            return result

        # Pick best candidate (highest confidence for now)
        best_candidate = max(person_result.candidates, key=lambda c: c.confidence)
        
        # 3. Face Recognition Guard
        face_result = None
        final_status = "PERSON_CANDIDATE"
        
        if not best_candidate.is_large_enough_for_face:
            final_status = "PERSON_CANDIDATE"
        else:
            face_result = await run_in_threadpool(
                self.face_service.verify_candidate,
                best_candidate,
                image_bytes,
            )
            final_status = face_result.status

        # 4. Update Global Detection State
        await self.detection_service.update_vision_state(
            db=db,
            status=final_status,
            candidate=best_candidate,
            face_result=face_result,
            source=source
        )

        result = VisionAnalysisResult(
            status=final_status,
            person_candidates=person_result.candidates,
            face_result=face_result,
            detection_state=self.detection_service.get_state().dict()
        )
        
        # 5. Robot Decision (Autonomous follow, etc.)
        await self.robot_decision_service.process_vision_result(result)
        
        return result
