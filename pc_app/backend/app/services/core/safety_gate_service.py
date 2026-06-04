from typing import Any, Dict
from app.services.core.telemetry_service import TelemetryService
from app.core.config import Settings

class SafetyGateService:
    DRIVE_COMMANDS = {
        "REMOTE_DRIVE",
        "SET_MOTOR_SPEED",
        "MOVE_FORWARD",
        "MOVE_BACKWARD",
        "TURN_LEFT",
        "TURN_RIGHT",
        "ROTATE_LEFT",
        "ROTATE_RIGHT",
    }
    SAFE_COMMANDS = {"STOP", "REMOTE_STOP", "EMERGENCY_STOP", "RESET_EMERGENCY"}
    DRIVE_ALLOWED_MODES = {"MANUAL_REMOTE", "LEARNING_MAP", "AUTO_SEARCH", "AUTO"}

    def __init__(self, telemetry_service: TelemetryService, settings: Settings):
        self._telemetry_service = telemetry_service
        self._settings = settings

    def validate_command(self, payload: Dict[str, Any]) -> bool:
        return bool(self.evaluate_command(payload)["allowed"])

    def evaluate_command(self, payload: Dict[str, Any]) -> dict[str, Any]:
        """
        Returns an explicit decision for whether a command is safe to send.
        """
        command = str(payload.get("command", "")).upper()
        if command in self.SAFE_COMMANDS:
            return {"allowed": True, "reason": "SAFE_COMMAND"}

        if command not in self.DRIVE_COMMANDS:
            return {"allowed": True, "reason": "NON_DRIVE_COMMAND"}

        telemetry = self._telemetry_service.latest_car_telemetry
        if not telemetry:
            return {"allowed": False, "reason": "TELEMETRY_MISSING"}

        if self._telemetry_service.car_telemetry_stale(self._settings.robot_telemetry_stale_ms):
            return {"allowed": False, "reason": "TELEMETRY_STALE"}

        if not self._telemetry_service.car_connected(self._settings.car_offline_timeout_seconds):
            return {"allowed": False, "reason": "ROBOT_OFFLINE"}

        mode = telemetry.get("mode")
        if mode not in self.DRIVE_ALLOWED_MODES:
            return {"allowed": False, "reason": "MODE_NOT_ALLOWED", "mode": mode}

        left_pwm = payload.get("left_motor_speed", 0)
        right_pwm = payload.get("right_motor_speed", 0)
        moving_forward = command in {"MOVE_FORWARD"} or left_pwm > 0 or right_pwm > 0
        moving_backward = command in {"MOVE_BACKWARD"} or left_pwm < 0 or right_pwm < 0

        if moving_forward and (telemetry.get("obstacle_front") or telemetry.get("forward_unsafe")):
            return {"allowed": False, "reason": "FORWARD_UNSAFE"}
            
        if moving_backward and (telemetry.get("obstacle_rear") or telemetry.get("backward_unsafe")):
            return {"allowed": False, "reason": "BACKWARD_UNSAFE"}

        if telemetry.get("cliff_detected"):
            return {"allowed": False, "reason": "CLIFF_DETECTED"}

        battery_voltage = telemetry.get("battery_voltage")
        if battery_voltage is not None and battery_voltage < 6.5:
            return {"allowed": False, "reason": "BATTERY_LOW"}

        return {"allowed": True, "reason": "SAFE"}
