from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/telemetry", tags=["telemetry"])


@router.get("/latest")
def get_latest_telemetry(request: Request) -> dict:
    telemetry_service = request.app.state.telemetry_service
    return {
        "car": telemetry_service.latest_car_telemetry,
        "joystick": telemetry_service.latest_joystick_telemetry,
        "events": telemetry_service.events,
    }
