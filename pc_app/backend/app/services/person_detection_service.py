from typing import Optional, List

from app.core.loggers import logger
from app.schemas.vision import PersonDetectionResult, PersonCandidate

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
        
        if HAS_ULTRALYTICS:
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

    def detect_persons(
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

        try:
            import cv2
            import numpy as np
        except ImportError as exc:
            return PersonDetectionResult(
                status="PROVIDER_NOT_READY",
                candidates=[],
                provider=self.provider_name,
                message=f"OpenCV/numpy dependency is not ready: {exc}"
            )
        
        # Load image
        if image_bytes:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif image_path:
            img = cv2.imread(image_path)
        else:
            return PersonDetectionResult(status="ERROR", message="No input image", candidates=[])

        if img is None:
            return PersonDetectionResult(status="ERROR", message="Failed to decode image", candidates=[])

        # Run inference
        results = self.model(img, verbose=False, classes=[0]) # Class 0 is person
        
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
