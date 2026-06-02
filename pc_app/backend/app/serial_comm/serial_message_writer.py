import json
import threading
from typing import Any

import serial


class SerialMessageWriter:
    def __init__(self, serial_connection: serial.Serial) -> None:
        self._serial_connection = serial_connection
        self._write_lock = threading.Lock()

    def write_json_line(self, payload: dict[str, Any]) -> None:
        encoded_payload = (json.dumps(payload, separators=(",", ":")) + "\n").encode(
            "utf-8"
        )
        with self._write_lock:
            self._serial_connection.write(encoded_payload)
            self._serial_connection.flush()
