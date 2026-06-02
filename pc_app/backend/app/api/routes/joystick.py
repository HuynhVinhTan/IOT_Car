from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/joystick", tags=["joystick"])


@router.get("/status")
def get_joystick_status(request: Request) -> dict:
    telemetry_service = request.app.state.telemetry_service
    settings = request.app.state.settings
    return {
        "connected": telemetry_service.joystick_connected(
            settings.joystick_offline_timeout_seconds
        ),
        "telemetry": telemetry_service.latest_joystick_telemetry,
    }
