from pydantic import BaseModel
from typing import Optional, List
import uuid

class PersonCandidate(BaseModel):
    bbox: list[float] # normalized [x1, y1, x2, y2]
    confidence: float
    distance_level: Optional[str] = "unknown" # far, mid, near
    is_large_enough_for_face: bool = False
    notes: Optional[str] = None

class PersonDetectionResult(BaseModel):
    status: str # OK, PROVIDER_NOT_READY, ERROR
    candidates: List[PersonCandidate] = []
    provider: str
    message: Optional[str] = None

class FaceRecognitionResult(BaseModel):
    status: str # TARGET_FOUND, UNKNOWN_PERSON, FACE_NOT_CLEAR, PROVIDER_NOT_READY, NO_TARGET
    target_person_id: Optional[uuid.UUID] = None
    display_name: Optional[str] = None
    confidence: float = 0.0
    threshold: float = 0.75
    bbox: Optional[dict] = None
    message: Optional[str] = None

class VisionAnalysisResult(BaseModel):
    status: str
    person_candidates: List[PersonCandidate] = []
    face_result: Optional[FaceRecognitionResult] = None
    detection_state: dict # Serialized DetectionState
    media_asset_id: Optional[uuid.UUID] = None
    message: Optional[str] = None
