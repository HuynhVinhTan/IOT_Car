from fastapi import APIRouter, Request

from app.schemas.route_segment import SelectSegmentRequest, HeadingHintRequest


router = APIRouter(prefix="/api/routes", tags=["route_segments"])


@router.get("/segments")
def get_segments(request: Request) -> list[dict]:
    return request.app.state.route_segment_service.get_segments()


@router.get("/current-selection")
def get_current_selection(request: Request) -> dict:
    return request.app.state.route_segment_service.get_current_selection()


@router.post("/select-segment")
def select_segment(request: Request, payload: SelectSegmentRequest) -> dict:
    return request.app.state.route_segment_service.select_segment(
        payload.segment_id, payload.confirm_on_segment
    )


@router.post("/cancel-segment")
def cancel_segment(request: Request) -> dict:
    return request.app.state.route_segment_service.cancel_segment()


@router.post("/auto-infer")
def auto_infer(request: Request) -> dict:
    return request.app.state.route_segment_service.auto_infer()


@router.post("/heading-hint")
def heading_hint(request: Request, payload: HeadingHintRequest) -> dict:
    return request.app.state.route_segment_service.heading_hint(
        payload.segment_id, payload.heading_hint_x, payload.heading_hint_y
    )
