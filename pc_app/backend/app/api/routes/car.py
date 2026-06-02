from fastapi import APIRouter, Request

from app.schemas.car_command import CarCommand, ModeRequest

router = APIRouter(prefix="/api/car", tags=["car"])


@router.get("/status")
def get_car_status(request: Request) -> dict:
    telemetry_service = request.app.state.telemetry_service
    settings = request.app.state.settings
    return {
        "connected": telemetry_service.car_connected(
            settings.car_offline_timeout_seconds
        ),
        "telemetry": telemetry_service.latest_car_telemetry,
    }


@router.post("/command")
def send_command(request: Request, command: CarCommand) -> dict:
    return request.app.state.car_control_service.send_command(command.to_payload())


@router.post("/mode")
def set_mode(request: Request, mode_request: ModeRequest) -> dict:
    return request.app.state.car_control_service.set_mode(mode_request.mode)


@router.post("/record/start")
def start_record(request: Request) -> dict:
    return request.app.state.car_control_service.send_command(
        {"command": "START_RECORD"}
    )


@router.post("/record/stop")
def stop_record(request: Request) -> dict:
    return request.app.state.car_control_service.send_command(
        {"command": "STOP_RECORD"}
    )


@router.post("/auto/start")
def start_auto(request: Request) -> dict:
    return request.app.state.car_control_service.send_command(
        {"command": "START_AUTO_SEARCH"}
    )


@router.post("/auto/stop")
def stop_auto(request: Request) -> dict:
    return request.app.state.car_control_service.send_command(
        {"command": "STOP_MISSION"}
    )


@router.post("/emergency-stop")
def emergency_stop(request: Request) -> dict:
    return request.app.state.car_control_service.send_command(
        {"command": "EMERGENCY_STOP"}
    )


@router.post("/remote-stop")
def remote_stop(request: Request) -> dict:
    return request.app.state.car_control_service.send_command(
        {"command": "REMOTE_STOP"}
    )


@router.post("/reset-emergency")
def reset_emergency(request: Request) -> dict:
    return request.app.state.car_control_service.send_command(
        {"command": "RESET_EMERGENCY"}
    )
