import time
from typing import Any


class TelemetryService:
    def __init__(self) -> None:
        self.latest_car_telemetry: dict[str, Any] | None = None
        self.latest_joystick_telemetry: dict[str, Any] | None = None
        self.latest_car_message_time: float = 0.0
        self.latest_joystick_message_time: float = 0.0
        self.events: list[dict[str, Any]] = []

    def update_car_message(self, message: dict[str, Any]) -> None:
        self.latest_car_message_time = time.monotonic()
        if message.get("type") == "car_telemetry":
            self.latest_car_telemetry = message
        elif message.get("type") in {"car_event", "command_ack", "serial_error"}:
            self.add_event(message)

    def update_telemetry(self, message: dict[str, Any]) -> None:
        self.update_car_message(message)

    def update_joystick_message(self, message: dict[str, Any]) -> None:
        self.latest_joystick_message_time = time.monotonic()
        if message.get("type") == "joystick_telemetry":
            self.latest_joystick_telemetry = message
        elif message.get("type") in {
            "joystick_command_ack",
            "remote_button_event",
            "serial_error",
        }:
            self.add_event(message)

    def car_connected(self, timeout_seconds: float) -> bool:
        return time.monotonic() - self.latest_car_message_time <= timeout_seconds

    def car_telemetry_age_ms(self) -> float | None:
        if self.latest_car_message_time <= 0.0:
            return None
        return (time.monotonic() - self.latest_car_message_time) * 1000.0

    def car_telemetry_stale(self, stale_after_ms: int) -> bool:
        age_ms = self.car_telemetry_age_ms()
        return age_ms is None or age_ms > stale_after_ms

    def joystick_connected(self, timeout_seconds: float) -> bool:
        return time.monotonic() - self.latest_joystick_message_time <= timeout_seconds

    def add_event(self, event_payload: dict[str, Any]) -> None:
        self.events.insert(0, event_payload)
        self.events = self.events[:100]

    def get_latest_telemetry(self) -> dict[str, Any] | None:
        return self.latest_car_telemetry

    def get_latest_joystick_telemetry(self) -> dict[str, Any] | None:
        return self.latest_joystick_telemetry
