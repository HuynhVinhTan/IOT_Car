from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/auto", tags=["auto"])


@router.post("/start")
def start_auto(request: Request) -> dict:
    return request.app.state.car_control_service.send_command(
        {"command": "START_AUTO_SEARCH"}
    )


@router.post("/stop")
def stop_auto(request: Request) -> dict:
    return request.app.state.car_control_service.send_command(
        {"command": "STOP_MISSION"}
    )
