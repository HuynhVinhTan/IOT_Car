from __future__ import annotations

from typing import Any, TYPE_CHECKING
from app.schemas.vision import FaceRecognitionResult, PersonCandidate

if TYPE_CHECKING:
    from app.services.face.face_registry_service import FaceRegistryService

import logging
from datetime import datetime
from insightface.app import FaceAnalysis

logger = logging.getLogger(__name__)

class FaceRecognitionService:
    def __init__(self, registry_service: FaceRegistryService):
        self.registry_service = registry_service
        self._ready = False
        self._model = None
        self._last_error = None
        self._model_name = "buffalo_l"
        self._provider = "CPUExecutionProvider"
        self._initialized_at = None

    async def initialize(self) -> None:
        try:
            logger.info("Initializing FaceRecognitionService...")
            self._model = FaceAnalysis(
                name=self._model_name,
                providers=[self._provider],
            )
            self._model.prepare(ctx_id=-1, det_size=(640, 640))
            self._ready = True
            self._initialized_at = datetime.now()
            logger.info("FaceRecognitionService initialized successfully.")
        except Exception as e:
            self._last_error = str(e)
            logger.error(f"Failed to initialize FaceRecognitionService: {e}")
            self._ready = False

    def get_status(self) -> dict:
        return {
            "ready": self._ready,
            "model_name": self._model_name,
            "provider": self._provider,
            "last_error": self._last_error,
            "initialized_at": self._initialized_at.isoformat() if self._initialized_at else None,
        }

    def is_ready(self) -> bool:
        return self._ready

    def verify_candidate(self, candidate: PersonCandidate, frame_data: Any = None) -> FaceRecognitionResult:
        """
        Only run face recognition if candidate is large enough and provider is ready.
        """
        if not self._ready:
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
        if not self._ready:
            return {"status": "PROVIDER_NOT_READY"}
        return {"status": "UNKNOWN_PERSON"}

    async def enroll_target(self, frame_data: bytes) -> Any:
        """
        Enroll a new face target from image bytes.
        Returns None if provider is not ready.
        """
        if not self._ready:
            return None
        return None

    async def build_cache(self, db: Any) -> None:
        """
        Refresh the internal face cache from the database.
        """
        pass
