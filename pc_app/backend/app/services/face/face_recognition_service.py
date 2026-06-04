from __future__ import annotations

from typing import Any, TYPE_CHECKING
from app.schemas.vision import FaceRecognitionResult, PersonCandidate

if TYPE_CHECKING:
    from app.services.face.face_registry_service import FaceRegistryService

class FaceRecognitionService:
    def __init__(self, registry_service: FaceRegistryService):
        self.registry_service = registry_service
        self.provider_ready = False

    def is_ready(self) -> bool:
        return self.provider_ready

    def verify_candidate(self, candidate: PersonCandidate, frame_data: Any = None) -> FaceRecognitionResult:
        """
        Only run face recognition if candidate is large enough and provider is ready.
        """
        if not self.provider_ready:
            return FaceRecognitionResult(
                status="PROVIDER_NOT_READY",
                message="Face embedding provider not initialized"
            )
        
        # Guard: Check if candidate is large enough/clear
        if not candidate.is_large_enough_for_face:
            return FaceRecognitionResult(
                status="FACE_NOT_CLEAR",
                message="Person candidate is too far or small for face recognition"
            )

        return FaceRecognitionResult(
            status="PROVIDER_NOT_READY",
            message="Face recognition provider is not implemented"
        )

    def verify_frame(self, frame_data: Any = None) -> Any:
        # Backward compatibility or direct frame scan (not recommended for robot)
        if not self.provider_ready:
            return {"status": "PROVIDER_NOT_READY"}
        return {"status": "UNKNOWN_PERSON"}

    async def enroll_target(self, frame_data: bytes) -> Any:
        """
        Enroll a new face target from image bytes.
        Returns None if provider is not ready.
        """
        if not self.provider_ready:
            return None
        return None

    async def build_cache(self, db: Any) -> None:
        """
        Refresh the internal face cache from the database.
        """
        pass
