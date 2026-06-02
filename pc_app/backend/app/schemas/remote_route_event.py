from pydantic import BaseModel


class RemoteRouteEvent(BaseModel):
    type: str = "remote_route_event"
    event: str
    timestamp_ms: int
    segment_index: int | None = None
    segment_id: str | None = None
    heading_hint_x: float | None = None
    heading_hint_y: float | None = None
