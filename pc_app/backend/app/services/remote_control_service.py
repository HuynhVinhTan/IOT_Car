from typing import Any

from app.core.config import Settings
from app.services.car_control_service import CarControlService
from app.services.telemetry_service import TelemetryService


class RemoteControlService:
    def __init__(
        self,
        car_control_service: CarControlService,
        telemetry_service: TelemetryService,
        settings: Settings,
    ) -> None:
        self._car_control_service = car_control_service
        self._telemetry_service = telemetry_service
        self._settings = settings

    def handle_remote_button_event(self, remote_button_event: dict[str, Any]) -> None:
        event_name = remote_button_event.get("event")
        if event_name == "mode_button_short_press":
            self._handle_short_press()
        elif event_name == "mode_button_long_press":
            self._handle_long_press()

    def _handle_short_press(self) -> None:
        car_telemetry = self._telemetry_service.latest_car_telemetry or {}
        current_mode = car_telemetry.get("mode", "IDLE")
        if current_mode == "EMERGENCY_STOP":
            self._telemetry_service.add_event(
                {
                    "type": "backend_event",
                    "event": "remote_button_ignored",
                    "reason": "EmergencyStop requires RESET_EMERGENCY",
                }
            )
            return
        if current_mode == "IDLE":
            self._car_control_service.set_mode("MANUAL_REMOTE")
        elif current_mode == "MANUAL_REMOTE":
            self._car_control_service.set_mode("AUTO_SEARCH")
        elif current_mode in {"AUTO_SEARCH", "RETURN_HOME", "LEARNING_MAP", "AUTO"}:
            self._car_control_service.send_command({"command": "REMOTE_STOP"})
            self._car_control_service.set_mode("MANUAL_REMOTE")
        else:
            self._car_control_service.set_mode("IDLE")

    def _handle_long_press(self) -> None:
        car_telemetry = self._telemetry_service.latest_car_telemetry or {}
        if car_telemetry.get("mode") == "EMERGENCY_STOP":
            self._telemetry_service.add_event(
                {
                    "type": "backend_event",
                    "event": "remote_button_ignored",
                    "reason": "Long press does not reset EmergencyStop",
                }
            )
            return
        self._car_control_service.send_command({"command": "REMOTE_STOP"})
        self._car_control_service.set_mode("IDLE")
