import json
import threading
from collections.abc import Callable
from typing import Any

import serial


JsonCallback = Callable[[dict[str, Any]], None]


class SerialMessageReader:
    def __init__(self, serial_connection: serial.Serial, source_name: str) -> None:
        self._serial_connection = serial_connection
        self._source_name = source_name
        self._reader_thread: threading.Thread | None = None
        self._running = False

    def start(self, on_message: JsonCallback) -> None:
        if self._running:
            return

        self._running = True
        self._reader_thread = threading.Thread(
            target=self._read_loop, args=(on_message,), daemon=True
        )
        self._reader_thread.start()

    def stop(self) -> None:
        self._running = False
        if self._reader_thread and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=1.0)

    def _read_loop(self, on_message: JsonCallback) -> None:
        while self._running and self._serial_connection.is_open:
            raw_line = (
                self._serial_connection.readline()
                .decode("utf-8", errors="ignore")
                .strip()
            )
            if not raw_line:
                continue

            try:
                on_message(json.loads(raw_line))
            except json.JSONDecodeError:
                on_message(
                    {
                        "type": "serial_error",
                        "source": self._source_name,
                        "raw": raw_line,
                    }
                )
