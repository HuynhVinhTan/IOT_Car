from pydantic import BaseModel


class RobotPose(BaseModel):
    x: float = 0.0
    y: float = 0.0
    heading_deg: float = 0.0


class RobotMapPosition(BaseModel):
    current_node: str | None = None
    current_segment_id: str | None = None
    target_node: str | None = None
    direction: str = "unknown"
    progress_ratio: float = 0.0
    position_source: str = "telemetry"
    updated_at_ms: int = 0


class CarTelemetry(BaseModel):
    type: str = "car_telemetry"
    timestamp_ms: int = 0
    board: str = "ESP32_WROOM"
    mode: str = "IDLE"
    left_motor_speed: int = 0
    right_motor_speed: int = 0
    distance_cm: float | None = None
    front_distance_cm: float | None = None
    left_distance_cm: float | None = None
    right_distance_cm: float | None = None
    rear_distance_cm: float | None = None
    obstacle_front: bool = False
    obstacle_left: bool = False
    obstacle_right: bool = False
    obstacle_rear: bool = False
    front_left_ground_cm: float | None = None
    front_right_ground_cm: float | None = None
    rear_left_ground_cm: float | None = None
    rear_right_ground_cm: float | None = None
    front_cliff_detected: bool = False
    rear_cliff_detected: bool = False
    cliff_detected: bool = False
    forward_unsafe: bool = False
    backward_unsafe: bool = False
    battery_voltage: float = 0.0
    battery_percent: int = 0
    lcd_status: str = "UNKNOWN"
    lcd_enabled: bool = False
    current_node: str = "UNKNOWN"
    home_node: str = "HOME"
    target_node: str = ""
    current_pose: RobotPose | None = None
    speed_value: float = 0.0
    obstacle_detected: bool = False
    is_recording: bool = False
    recorded_path_points: int = 0
    is_auto_running: bool = False
    person_detected: bool = False
    emergency_reason: str = ""
    control_source: str = "NONE"
