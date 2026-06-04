from app.services.robot.car_control_service import CarControlService
from app.services.robot.telemetry_service import TelemetryService
from app.serial_comm.joystick_serial_client import JoystickSerialClient
from app.services.robot.remote_control_service import RemoteControlService
from app.services.route_segment_service import RouteSegmentService

class JoystickService:
    def __init__(
        self,
        telemetry_service: TelemetryService,
        car_control_service: CarControlService,
        joystick_serial_client: JoystickSerialClient,
        remote_control_service: RemoteControlService,
        route_segment_service: RouteSegmentService,
    ) -> None:
        self._telemetry_service = telemetry_service
        self._car_control_service = car_control_service
        self._joystick_serial_client = joystick_serial_client
        self._remote_control_service = remote_control_service
        self._route_segment_service = route_segment_service

    def handle_joystick_message(self, message: dict) -> None:
        self._telemetry_service.update_joystick_message(message)
        if message.get("type") == "joystick_telemetry":
            self._car_control_service.handle_joystick_telemetry(message)
        elif message.get("type") == "remote_button_event":
            self._remote_control_service.handle_remote_button_event(message)
        elif message.get("type") == "remote_route_event":
            self._handle_remote_route_event(message)

    def _handle_remote_route_event(self, message: dict) -> None:
        event = message.get("event")
        if not event:
            return

        if event == "previous_segment" or event == "next_segment":
            segments = self._route_segment_service.get_segments()
            if not segments:
                return
            enabled_segments = [s for s in segments if s.get("is_enabled") and not s.get("is_blocked")]
            if not enabled_segments:
                return

            current_sel = self._route_segment_service.get_current_selection()
            selected_id = current_sel.get("selected_segment_id")
            idx = -1
            if selected_id:
                for i, s in enumerate(enabled_segments):
                    if s["segment_id"] == selected_id:
                        idx = i
                        break

            if event == "previous_segment":
                new_idx = (idx - 1) % len(enabled_segments) if idx != -1 else len(enabled_segments) - 1
            else:
                new_idx = (idx + 1) % len(enabled_segments) if idx != -1 else 0

            self._route_segment_service.select_segment(enabled_segments[new_idx]["segment_id"], False)

        elif event == "segment_selected":
            # the joystick user pressed confirm (short press)
            current_sel = self._route_segment_service.get_current_selection()
            selected_id = current_sel.get("selected_segment_id")
            if selected_id:
                self._route_segment_service.select_segment(selected_id, True)

        elif event == "segment_command_cancelled":
            self._route_segment_service.cancel_segment()

        elif event == "auto_infer_segment_requested":
            self._route_segment_service.auto_infer()

        elif event == "segment_heading_hint":
            current_sel = self._route_segment_service.get_current_selection()
            selected_id = current_sel.get("selected_segment_id")
            if selected_id:
                x = message.get("heading_hint_x", 0.0)
                y = message.get("heading_hint_y", 0.0)
                self._route_segment_service.heading_hint(selected_id, x, y)

    def send_alert_command(self, payload: dict) -> dict:
        self._joystick_serial_client.send_command(payload)
        return {"sent": True, "payload": payload}

    def start_person_found_alert(self) -> dict:
        return self.send_alert_command({"command": "START_PERSON_FOUND_ALERT"})

    def stop_person_found_alert(self) -> dict:
        return self.send_alert_command({"command": "STOP_PERSON_FOUND_ALERT"})

    def play_alert_once(self) -> dict:
        return self.send_alert_command({"command": "PLAY_ALERT_ONCE"})

    def set_alert_enabled(self, enabled: bool) -> dict:
        return self.send_alert_command(
            {"command": "SET_ALERT_ENABLED", "enabled": enabled}
        )

    def alert_status(self) -> dict:
        joystick_telemetry = self._telemetry_service.latest_joystick_telemetry or {}
        return {
            "alert_siren_active": joystick_telemetry.get("alert_siren_active", False),
            "alert_enabled": joystick_telemetry.get("alert_enabled", False),
            "telemetry": joystick_telemetry or None,
        }

    def get_latest_telemetry(self) -> dict | None:
        return self._telemetry_service.latest_joystick_telemetry
