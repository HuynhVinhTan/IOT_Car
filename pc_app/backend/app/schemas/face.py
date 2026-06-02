from pydantic import BaseModel
from typing import Optional, List

class FaceTarget(BaseModel):
    target_person_id: str
    display_name: str
    image_paths: List[str] = []
    embedding_path: Optional[str] = None
    created_at_ms: int
    is_active: bool = True
    notes: Optional[str] = None

class FaceTargetCreate(BaseModel):
    display_name: str
    notes: Optional[str] = None

class FaceStatus(BaseModel):
    status: str
    registered_targets: int
    embedding_provider_ready: bool
    message: str

class FaceVerifyResponse(BaseModel):
    person_found: bool
    target_person_id: Optional[str] = None
    display_name: Optional[str] = None
    confidence: float
    threshold: float
    status: Optional[str] = None
    reason: Optional[str] = None
