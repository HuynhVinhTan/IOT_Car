from collections.abc import Callable
from typing import Any

import serial

from app.serial_comm.serial_message_reader import SerialMessageReader
from app.serial_comm.serial_message_writer import SerialMessageWriter


JsonCallback = Callable[[dict[str, Any]], None]


class JoystickSerialClient:
    def __init__(self, port: str, baud_rate: int) -> None:
        self._port = port
        self._baud_rate = baud_rate
        self._serial: serial.Serial | None = None
        self._reader: SerialMessageReader | None = None
        self._writer: SerialMessageWriter | None = None
        self._running = False

    @property
    def connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def start(self, on_message: JsonCallback) -> None:
        if self._running:
            return

        try:
            self._serial = serial.Serial(self._port, self._baud_rate, timeout=1)
        except serial.SerialException as exc:
            on_message(
                {
                    "type": "serial_error",
                    "source": "joystick",
                    "message": str(exc),
                }
            )
            return

        self._running = True
        self._reader = SerialMessageReader(self._serial, "joystick")
        self._writer = SerialMessageWriter(self._serial)
        self._reader.start(on_message)

    def send_command(self, payload: dict[str, Any]) -> None:
        if not self.connected or self._writer is None:
            raise RuntimeError("Joystick ESP8266 serial is not connected")

        self._writer.write_json_line(payload)

    def stop(self) -> None:
        self._running = False
        if self._reader is not None:
            self._reader.stop()
        if self._serial is not None and self._serial.is_open:
            self._serial.close()
        self._writer = None
