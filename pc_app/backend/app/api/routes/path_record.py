from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/path-record", tags=["path-record"])


@router.post("/start")
def start_record(request: Request) -> dict:
    return request.app.state.car_control_service.send_command(
        {"command": "START_RECORD"}
    )


@router.post("/stop")
def stop_record(request: Request) -> dict:
    return request.app.state.car_control_service.send_command(
        {"command": "STOP_RECORD"}
    )


@router.post("/clear")
def clear_recorded_path(request: Request) -> dict:
    return request.app.state.car_control_service.send_command(
        {"command": "CLEAR_PATH"}
    )
