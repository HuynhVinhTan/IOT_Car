from pydantic import BaseModel


class DetectionEvent(BaseModel):
    id: str
    type: str = "detection_event"
    event: str
    detected_at: str
    confidence: float | None = None
    snapshot_path: str | None = None
    car_mode: str | None = None
    distance_cm: float | None = None
    car_status: str | None = None
