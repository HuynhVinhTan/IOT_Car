from typing import Any

from app.core.config import Settings
from app.serial_comm.car_serial_client import CarSerialClient
from app.services.robot.telemetry_service import TelemetryService
from app.services.safety_gate_service import SafetyGateService


class CarControlService:
    def __init__(
        self,
        car_serial_client: CarSerialClient,
        telemetry_service: TelemetryService,
        safety_gate_service: SafetyGateService,
        settings: Settings,
    ) -> None:
        self._car_serial_client = car_serial_client
        self._telemetry_service = telemetry_service
        self._safety_gate_service = safety_gate_service
        self._settings = settings
        self.latest_remote_drive_command: dict[str, Any] | None = None
        self._command_callback = None

    def set_command_callback(self, callback):
        self._command_callback = callback

    def send_command(self, payload: dict[str, Any]) -> dict[str, Any]:
        safety_decision = self._safety_gate_service.evaluate_command(payload)
        if not safety_decision["allowed"]:
            return {
                "sent": False,
                "allowed": False,
                "status": "BLOCKED",
                "reason": safety_decision["reason"],
                "payload": payload,
            }

        # Send via Serial (Legacy)
        try:
            self._car_serial_client.send_command(payload)
        except Exception:
            pass
        
        # Send via WebSocket (New)
        if self._command_callback:
            self._command_callback(payload)
            
        return {"sent": True, "allowed": True, "status": "SENT", "payload": payload}


    def set_mode(self, mode: str) -> dict[str, Any]:
        return self.send_command({"command": "SET_MODE", "mode": mode})

    def handle_joystick_telemetry(self, joystick_telemetry: dict[str, Any]) -> None:
        car_telemetry = self._telemetry_service.latest_car_telemetry or {}
        if car_telemetry.get("mode") != "MANUAL_REMOTE":
            return

        if car_telemetry.get("emergency_reason"):
            return

        if joystick_telemetry.get("deadzone_applied", True):
            command_payload = {"command": "REMOTE_STOP"}
        else:
            command_payload = self._joystick_to_remote_drive(joystick_telemetry)

        self.latest_remote_drive_command = command_payload
        self.send_command(command_payload)

    def _joystick_to_remote_drive(
        self, joystick_telemetry: dict[str, Any]
    ) -> dict[str, Any]:
        normalized_x = float(joystick_telemetry.get("normalized_x", 0.0))
        normalized_y = float(joystick_telemetry.get("normalized_y", 0.0))

        left_speed = normalized_y + normalized_x
        right_speed = normalized_y - normalized_x
        max_magnitude = max(abs(left_speed), abs(right_speed), 1.0)

        left_speed = left_speed / max_magnitude
        right_speed = right_speed / max_magnitude
        max_motor_speed = self._settings.remote_drive_max_motor_speed

        return {
            "command": "REMOTE_DRIVE",
            "left_motor_speed": int(left_speed * max_motor_speed),
            "right_motor_speed": int(right_speed * max_motor_speed),
        }
