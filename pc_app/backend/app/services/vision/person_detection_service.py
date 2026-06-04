from typing import Optional, List

from app.core.loggers import logger
from app.schemas.vision import PersonDetectionResult, PersonCandidate

from app.core.config import settings

try:
    from ultralytics import YOLO
    HAS_ULTRALYTICS = True
except ImportError:
    HAS_ULTRALYTICS = False

class PersonDetectionService:
    def __init__(self):
        self.provider_ready = False
        self.provider_name = "YOLOv8n"
        self.model = None
        
        if HAS_ULTRALYTICS and settings.enable_person_detection:
            self._init_yolo()

    def _init_yolo(self):
        try:
            # Load model (will download if not exists)
            self.model = YOLO("yolov8n.pt")
            self.provider_ready = True
            logger("YOLOv8n Person Detector Ready")
        except Exception as e:
            logger(f"YOLO Init Error: {e}")
            self.provider_ready = False

    def is_ready(self) -> bool:
        return self.provider_ready

    async def detect_persons(
        self, 
        image_path: Optional[str] = None, 
        image_bytes: Optional[bytes] = None
    ) -> PersonDetectionResult:
        if not self.provider_ready or self.model is None:
            return PersonDetectionResult(
                status="PROVIDER_NOT_READY",
                candidates=[],
                provider=self.provider_name,
                message="YOLOv8n not ready or ultralytics not installed"
            )

        import asyncio
        import cv2
        import numpy as np

        def _process():
            # Load image
            if image_bytes:
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            elif image_path:
                img = cv2.imread(image_path)
            else:
                return None, "No input image"

            if img is None:
                return None, "Failed to decode image"

            # Run inference
            results = self.model(img, verbose=False, classes=[0]) # Class 0 is person
            return (results, img), None

        results_data, error = await asyncio.to_thread(_process)
        if error:
            return PersonDetectionResult(status="ERROR", message=error, candidates=[])

        results, img = results_data
        
        candidates = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0].cpu().numpy() # [x1, y1, x2, y2]
                conf = float(box.conf[0])
                
                # Normalize coordinates (0.0 to 1.0)
                h, w = img.shape[:2]
                normalized_bbox = [
                    float(b[0] / w), float(b[1] / h),
                    float(b[2] / w), float(b[3] / h)
                ]
                
                candidates.append(PersonCandidate(
                    confidence=conf,
                    bbox=normalized_bbox,
                    is_large_enough_for_face=(conf > 0.6) # Threshold for face attempt
                ))

        status = "OK" if candidates else "NO_PERSON"
        return PersonDetectionResult(
            status=status,
            candidates=candidates,
            provider=self.provider_name,
            message=f"Found {len(candidates)} persons"
        )
