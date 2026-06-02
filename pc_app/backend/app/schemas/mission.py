from pydantic import BaseModel

class DetectionState(BaseModel):
    status: str = "IDLE" # IDLE, NO_PERSON, PERSON_CANDIDATE, FACE_VISIBLE, FACE_NOT_CLEAR, TARGET_FOUND, UNKNOWN_PERSON, TARGET_LOST, PROVIDER_NOT_READY, CAMERA_NOT_READY
    object_found: bool = False
    object_type: str = "unknown"
    confidence: float = 0.0
    detected_at_ms: int = 0
    detected_node: str | None = None
    detected_segment_id: str | None = None
    follow_state: str = "idle"
    message: str = "Waiting"
    
    # New fields for vision pipeline
    is_target_found: bool = False
    last_person_bbox: dict | None = None # {x, y, w, h}
    last_face_bbox: dict | None = None # {x, y, w, h}
    target_person_id: str | None = None
    display_name: str | None = None

class MissionState(BaseModel):
    mission_mode: str = "IDLE"
    current_node: str = "UNKNOWN"
    home_node: str = "HOME"
    target_node: str = ""
    planned_path: list[str] = []
    coverage_progress: float = 0.0
    detection_state: DetectionState = DetectionState()
