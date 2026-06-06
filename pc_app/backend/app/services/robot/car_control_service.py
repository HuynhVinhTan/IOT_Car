import asyncio
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

    # --- BƯỚC 3: THÊM LOG ĐỂ TEST ĐỘC LẬP TẠI ĐÂY ---
    async def drive_timed(
        self,
        duration_ms: int,
        left_speed: int = 160,
        right_speed: int = 160,
    ) -> None:
        """
        Put the car in MANUAL_REMOTE, pump REMOTE_DRIVE for `duration_ms`,
        then send REMOTE_STOP. Designed to be awaited from an asyncio task.
        """
        # In ra Terminal Uvicorn để verify luồng tính toán thời gian từ API chuyển xuống
        print(f"\n🚀 [TEST LOG] drive_timed() được gọi thành công!")
        print(f"⏱️  Thời gian chạy dự kiến: {duration_ms} ms (left: {left_speed}, right: {right_speed})\n")

        self.set_mode("MANUAL_REMOTE")
        await asyncio.sleep(0.05)  # give ESP32 time to switch mode

        deadline = asyncio.get_event_loop().time() + duration_ms / 1000.0
        while asyncio.get_event_loop().time() < deadline:
            self.send_command({
                "command": "REMOTE_DRIVE",
                "left_motor_speed": left_speed,
                "right_motor_speed": right_speed,
            })
            await asyncio.sleep(0.08)  # ~12 Hz pump, within COMMAND_TIMEOUT_MS=1000

        self.send_command({"command": "REMOTE_STOP"})
        print(f"🛑 [TEST LOG] Hết thời gian {duration_ms}ms -> Đã gửi lệnh REMOTE_STOP dừng xe ngầm.")

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