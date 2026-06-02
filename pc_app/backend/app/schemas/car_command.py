from typing import Any

from pydantic import BaseModel, Field


class CarCommand(BaseModel):
    command: str
    mode: str | None = None
    left_motor_speed: int | None = Field(default=None, ge=-255, le=255)
    right_motor_speed: int | None = Field(default=None, ge=-255, le=255)
    detected: bool | None = None

    def to_payload(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)


class ModeRequest(BaseModel):
    mode: str
