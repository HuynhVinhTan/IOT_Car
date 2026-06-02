from pydantic import BaseModel
from typing import Optional, List

class TrainingSession(BaseModel):
    session_id: str
    session_name: str
    map_id: str = "default_map"
    segment_id: str
    direction: str
    start_node: str
    target_node: str
    status: str = "RECORDING" # RECORDING, STOPPED, EXPORTED
    record_camera: bool = True
    record_telemetry: bool = True
    record_joystick: bool = True
    sample_count: int = 0
    created_at_ms: int
    stopped_at_ms: Optional[int] = None
    output_dir: str
    notes: Optional[str] = None

class TrainingSample(BaseModel):
    sample_id: str
    session_id: str
    timestamp_ms: int
    image_path: Optional[str] = None
    segment_id: str
    direction: str
    current_node: str
    current_segment_id: Optional[str] = None
    target_node: str
    joystick_x: float
    joystick_y: float
    left_motor_speed: int
    right_motor_speed: int
    front_distance_cm: Optional[float] = None
    left_distance_cm: Optional[float] = None
    right_distance_cm: Optional[float] = None
    rear_distance_cm: Optional[float] = None
    forward_unsafe: bool = False
    backward_unsafe: bool = False
    object_found: bool = False
    label_quality: int = 100
    notes: Optional[str] = None

class TrainingSessionStartRequest(BaseModel):
    session_name: str
    map_id: str = "default_map"
    segment_id: str
    direction: str
    start_node: str
    target_node: str
    record_camera: bool = True
    record_telemetry: bool = True
    record_joystick: bool = True
    notes: Optional[str] = None

class TrainingExportRequest(BaseModel):
    session_id: str
    format: str = "folder_manifest"

class TrainingStatus(BaseModel):
    status: str
    current_session_id: Optional[str] = None
    dataset_ready: bool = False
    sample_count: int = 0
    message: str
