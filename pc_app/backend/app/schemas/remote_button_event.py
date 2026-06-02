from pydantic import BaseModel


class RemoteButtonEvent(BaseModel):
    type: str = "remote_button_event"
    event: str
    timestamp_ms: int = 0
