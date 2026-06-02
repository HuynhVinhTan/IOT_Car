from pydantic import BaseModel


class RouteSegment(BaseModel):
    segment_id: str
    from_node: str
    to_node: str
    label: str
    is_enabled: bool = True
    is_visited: bool = False
    is_blocked: bool = False


class RouteSelectionState(BaseModel):
    selected_segment_id: str | None = None
    current_segment_id: str | None = None
    current_node: str | None = None
    target_node: str | None = None
    localization_source: str = "NONE"
    localization_confidence: str = "LOW"
    heading_hint_x: float | None = None
    heading_hint_y: float | None = None
    accepted: bool = False
    reason: str = ""


class RouteGuidanceDecision(BaseModel):
    accepted: bool = False
    reason: str = ""
    segment_id: str | None = None
    current_segment_id: str | None = None
    target_node: str | None = None
    confidence: float = 0.0
    heading_hint_x: float | None = None
    heading_hint_y: float | None = None
    safety_status: str = "UNKNOWN"


class SelectSegmentRequest(BaseModel):
    segment_id: str
    confirm_on_segment: bool = False


class HeadingHintRequest(BaseModel):
    segment_id: str
    heading_hint_x: float
    heading_hint_y: float
