export type DriveMode =
  | "IDLE"
  | "MANUAL_REMOTE"
  | "AUTO_SEARCH"
  | "RETURN_HOME"
  | "LEARNING_MAP"
  | "STATUS_DISPLAY"
  | "EMERGENCY_STOP";

export interface RobotPose {
  x: number;
  y: number;
  heading_deg: number;
}

export interface RobotMapPosition {
  current_node: string | null;
  current_segment_id: string | null;
  target_node: string | null;
  direction: string;
  progress_ratio: number;
  position_source: string;
  updated_at_ms: number;
}

export interface DetectionState {
  object_found: boolean;
  object_type: string;
  confidence: number;
  detected_at_ms: number;
  detected_node: string | null;
  detected_segment_id: string | null;
  follow_state: string;
  message: string;
}

export interface MissionState {
  mission_mode: string;
  current_node: string;
  home_node: string;
  target_node: string;
  planned_path: string[];
  coverage_progress: number;
  detection_state: DetectionState;
}

export interface CarTelemetry {
  type: "car_telemetry";
  timestamp_ms: number;
  board: "ESP32_WROOM";
  mode: DriveMode;
  battery_voltage?: number;
  battery_percent?: number;
  lcd_status?: string;
  lcd_enabled?: boolean;
  current_node?: string;
  home_node?: string;
  target_node?: string;
  current_pose?: RobotPose | null;
  robot_position?: RobotMapPosition;
  mission_state?: MissionState;
  visited_nodes?: string[];
  coverage_progress?: number;
  left_motor_speed: number;
  right_motor_speed: number;
  distance_cm: number | null;
  front_distance_cm?: number | null;
  left_distance_cm?: number | null;
  right_distance_cm?: number | null;
  rear_distance_cm?: number | null;
  obstacle_front?: boolean;
  obstacle_left?: boolean;
  obstacle_right?: boolean;
  obstacle_rear?: boolean;
  front_left_ground_cm?: number | null;
  front_right_ground_cm?: number | null;
  rear_left_ground_cm?: number | null;
  rear_right_ground_cm?: number | null;
  front_cliff_detected?: boolean;
  rear_cliff_detected?: boolean;
  cliff_detected?: boolean;
  forward_unsafe?: boolean;
  backward_unsafe?: boolean;
  speed_value: number;
  obstacle_detected: boolean;
  is_recording: boolean;
  recorded_path_points: number;
  is_auto_running: boolean;
  person_detected: boolean;
  emergency_reason: string;
  control_source: string;
}
