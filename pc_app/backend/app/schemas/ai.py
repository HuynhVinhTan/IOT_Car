from pydantic import BaseModel
from typing import Optional

class AIStatus(BaseModel):
    status: str
    camera_connected: bool
    segment_model_loaded: bool
    face_model_loaded: bool
    dataset_ready: bool
    message: str

class SegmentAIStatus(BaseModel):
    status: str
    model_loaded: bool
    model_version: Optional[str] = None
    reason: Optional[str] = None

class SegmentPrediction(BaseModel):
    segment_id: str
    direction: str
    confidence: float
    model_version: str
    status: Optional[str] = None
    reason: Optional[str] = None
