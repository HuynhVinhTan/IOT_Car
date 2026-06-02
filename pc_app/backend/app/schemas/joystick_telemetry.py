from pydantic import BaseModel


class JoystickTelemetry(BaseModel):
    type: str = "joystick_telemetry"
    timestamp_ms: int = 0
    board: str = "ESP8266MOD"
    ads1115_connected: bool = False
    raw_x: int = 0
    raw_y: int = 0
    normalized_x: float = 0.0
    normalized_y: float = 0.0
    deadzone_applied: bool = True
    button_pressed: bool = False
    joystick_button_pressed: bool = False
    remote_mode_button_pressed: bool = False
    alert_siren_active: bool = False
    alert_enabled: bool = True
    warning: str | None = None
