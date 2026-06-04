from typing import Optional

class RobotModeService:
    def __init__(self) -> None:
        self._current_mode: str = "MANUAL_REMOTE"

    def get_mode(self) -> str:
        return self._current_mode

    def set_mode(self, mode: str) -> None:
        self._current_mode = mode

__all__ = ["RobotModeService"]