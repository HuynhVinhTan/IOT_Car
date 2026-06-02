from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/joystick-alert", tags=["joystick-alert"])


class AlertEnabledRequest(BaseModel):
    enabled: bool


@router.get("/status")
def get_joystick_alert_status(request: Request) -> dict:
    return request.app.state.joystick_service.alert_status()


@router.post("/start")
def start_joystick_alert(request: Request) -> dict:
    return request.app.state.joystick_service.start_person_found_alert()


@router.post("/stop")
def stop_joystick_alert(request: Request) -> dict:
    return request.app.state.joystick_service.stop_person_found_alert()


@router.post("/test")
def test_joystick_alert(request: Request) -> dict:
    return request.app.state.joystick_service.play_alert_once()


@router.post("/enabled")
def set_joystick_alert_enabled(
    request: Request, payload: AlertEnabledRequest
) -> dict:
    return request.app.state.joystick_service.set_alert_enabled(payload.enabled)
