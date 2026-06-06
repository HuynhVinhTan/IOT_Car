from __future__ import annotations

from typing import Any, TYPE_CHECKING
from app.schemas.vision import FaceRecognitionResult, PersonCandidate

if TYPE_CHECKING:
    from app.services.face.face_registry_service import FaceRegistryService

import logging
from datetime import datetime

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

    def _get_app(self):
        if self._model is None:
            import traceback
            stack = traceback.format_stack()
            logger.info(f"Lazy-loading FaceAnalysis model... Caller stack:\n{''.join(stack)}")
            
            from insightface.app import FaceAnalysis
            self._model = FaceAnalysis(
                name=self._model_name,
                providers=[self._provider],
            )
            self._model.prepare(ctx_id=-1, det_size=(640, 640))
            self._ready = True
            self._initialized_at = datetime.now()
            logger.info("FaceAnalysis model loaded successfully.")
        return self._model

    async def initialize(self) -> None:
        # No-op for lazy loading, model will be loaded on first use
        logger.info("FaceRecognitionService ready for lazy loading.")
        self._ready = True

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

        app = self._get_app()
        return FaceRecognitionResult(
            status="PROVIDER_NOT_READY",
            message="Face recognition provider is not implemented"
        )

    def verify_frame(self, frame_data: Any = None) -> Any:
        # Backward compatibility or direct frame scan (not recommended for robot)
        if not self._ready:
            return {"status": "PROVIDER_NOT_READY"}
        app = self._get_app()
        return {"status": "UNKNOWN_PERSON"}

    def _decode_image_bytes(self, image_bytes: bytes):
        import cv2
        import numpy as np
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Invalid image file. Could not decode uploaded image.")
        return image

    async def enroll_target(self, frame_data: bytes) -> Any:
        """
        Enroll a new face target from image bytes.
        Returns None if provider is not ready.
        """
        if not self._ready:
            return None

        import asyncio
        app = await asyncio.to_thread(self._get_app)
        
        try:
            img = await asyncio.to_thread(self._decode_image_bytes, frame_data)
        except ValueError as e:
            logger.error(f"Failed to decode image: {e}")
            raise e
            
        logger.info("face enroll decoded image shape=%s", img.shape)
        
        # Try detection with default 640x640 det_size
        faces = await asyncio.to_thread(app.get, img)
        logger.info("face enroll detected face_count=%s", len(faces))
        if len(faces) > 0:
            main_face = faces[0]
            logger.info("face bbox=%s score=%s", getattr(main_face, "bbox", None), getattr(main_face, "det_score", None))
        
        if len(faces) == 0:
            # Try 320x320
            logger.info("Retrying with det_size=(320, 320)")
            await asyncio.to_thread(app.prepare, ctx_id=-1, det_size=(320, 320))
            faces = await asyncio.to_thread(app.get, img)
            logger.info("face enroll detected face_count=%s", len(faces))
            if len(faces) > 0:
                main_face = faces[0]
                logger.info("face bbox=%s score=%s", getattr(main_face, "bbox", None), getattr(main_face, "det_score", None))
            # Restore 640x640 for normal operation
            await asyncio.to_thread(app.prepare, ctx_id=-1, det_size=(640, 640))
        
        if len(faces) == 0:
            return None
            
        # Get the largest face
        faces = sorted(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), reverse=True)
        main_face = faces[0]
        
        return main_face.embedding

    async def build_cache(self, db: Any) -> None:
        """
        Refresh the internal face cache from the database.
        """
        pass
