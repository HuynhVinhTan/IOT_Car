export interface JoystickTelemetry {
  type: "joystick_telemetry";
  timestamp_ms: number;
  board: "ESP8266MOD";
  ads1115_connected?: boolean;
  raw_x: number;
  raw_y: number;
  normalized_x: number;
  normalized_y: number;
  deadzone_applied: boolean;
  button_pressed: boolean;
  joystick_button_pressed?: boolean;
  remote_mode_button_pressed?: boolean;
  alert_siren_active?: boolean;
  alert_enabled?: boolean;
  warning?: string | null;
}
