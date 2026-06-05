from fastapi import APIRouter, Request

from app.schemas.car_command import CarCommand, ModeRequest

router = APIRouter(prefix="/api/car", tags=["car"])


@router.get("/status")
def get_car_status(request: Request) -> dict:
    telemetry_service = request.app.state.telemetry_service
    settings = request.app.state.settings
    connected = telemetry_service.car_connected(settings.car_offline_timeout_seconds)
    telemetry = telemetry_service.latest_car_telemetry
    
    return {
        "connected": connected,
        "car_id": getattr(settings, "car_controller_id", "car_controller_01"),
        "mode": telemetry.get("mode", "UNKNOWN") if telemetry else "UNKNOWN",
        "last_seen_ms": telemetry.get("timestamp_ms", 0) if telemetry else 0,
        "latest_telemetry": telemetry
    }


async def send_command_to_car(request: Request, payload: dict) -> dict:
    from app.core.loggers import logger
    
    telemetry_service = request.app.state.telemetry_service
    settings = request.app.state.settings
    
    # Use the same connection check as /status
    if not telemetry_service.car_connected(settings.car_offline_timeout_seconds):
        return {"ok": False, "reason": "car_controller_not_connected"}

    ws = getattr(request.app.state, "car_ws", None)
    if ws is None:
        return {"ok": False, "reason": "car_controller_not_connected"}

    logger.info(f"Forwarding payload to car: {payload}")
    try:
        await ws.send_json(payload)
        return {
            "ok": True,
            "forwarded": True,
            "payload": payload
        }
    except Exception as exc:
        logger.error(f"Failed to forward command: {exc}")
        request.app.state.car_ws_connected = False
        request.app.state.car_ws = None
        return {
            "ok": False,
            "reason": "car_command_forward_failed",
            "detail": str(exc)
        }

@router.post("/command")
async def send_command(request: Request, command: CarCommand) -> dict:
    telemetry_service = request.app.state.telemetry_service
    settings = request.app.state.settings
    
    # Check if car is connected
    if not telemetry_service.car_connected(settings.car_offline_timeout_seconds):
        return {"ok": False, "reason": "car_controller_not_connected"}
        
    # Check mode
    latest = telemetry_service.latest_car_telemetry
    mode = latest.get("mode") if latest else "IDLE"
    
    payload = command.to_payload()
    cmd_type = payload.get("command")
    
    if cmd_type != "REMOTE_STOP" and mode not in ["MANUAL_REMOTE", "SERVER_CONTROL"]:
        return {
            "ok": False, 
            "reason": "car_not_in_server_control_mode",
            "current_mode": mode
        }
        
    # Validate speeds
    if cmd_type == "REMOTE_DRIVE":
        left = payload.get("left_motor_speed", 0)
        right = payload.get("right_motor_speed", 0)
        if not (-255 <= left <= 255 and -255 <= right <= 255):
            return {"ok": False, "reason": "speed_out_of_range"}
    
    # Map to firmware schema
    if cmd_type == "REMOTE_STOP":
        firmware_payload = {"type": "REMOTE_STOP", "source": "backend_api"}
    elif cmd_type == "REMOTE_DRIVE":
        firmware_payload = {
            "type": "REMOTE_DRIVE",
            "left_motor_speed": payload.get("left_motor_speed", 0),
            "right_motor_speed": payload.get("right_motor_speed", 0),
            "source": "backend_api"
        }
    else:
        firmware_payload = {"type": cmd_type, "source": "backend_api"}
            
    return await send_command_to_car(request, firmware_payload)


@router.post("/mode")
async def set_mode(request: Request, mode_request: ModeRequest) -> dict:
    telemetry_service = request.app.state.telemetry_service
    settings = request.app.state.settings

    # Check if car is connected
    if not telemetry_service.car_connected(settings.car_offline_timeout_seconds):
        return {"ok": False, "reason": "car_controller_not_connected"}

    req_mode = mode_request.mode.lower()
    
    if req_mode == "autonomous":
        import os
        from app.core.loggers import logger
        
        import pathlib
        BASE_DIR = pathlib.Path(__file__).parent.parent.parent.parent
        DATA_DIR = BASE_DIR / "data"
        MAPS_DIR = DATA_DIR / "maps"
        
        # Check if active map exists
        active_map_file = DATA_DIR / "active_map.txt"
        if not active_map_file.exists():
            logger.warning("No active map set for autonomous mode")
            return {"ok": False, "reason": "no_active_map", "detail": "Please select an active map first"}
        
        try:
            with open(active_map_file, "r") as f:
                active_map_id = f.read().strip()
        except Exception as e:
            logger.error(f"Failed to read active map: {e}")
            return {"ok": False, "reason": "failed_to_read_active_map"}
        
        # Verify active map file exists
        active_map_path = MAPS_DIR / f"{active_map_id}.json"
        if not active_map_path.exists():
            logger.warning(f"Active map {active_map_id} not found")
            return {"ok": False, "reason": "active_map_not_found", "active_map_id": active_map_id}
        
        try:
            import json
            with open(active_map_path, "r") as f:
                active_map = json.load(f)
            logger.info(f"Using active map for autonomous: {active_map_id}")
        except Exception as e:
            logger.error(f"Failed to load active map: {e}")
            return {"ok": False, "reason": "failed_to_load_active_map"}

    # Map frontend friendly names to firmware drive modes
    mode_mapping = {
        "server_control": "MANUAL_REMOTE",
        "manual_remote": "MANUAL_REMOTE",
        "idle": "IDLE",
        "autonomous": "AUTO_SEARCH",
        "auto": "AUTO_SEARCH"
    }

    # Handle EMERGENCY_STOP special case
    if req_mode == "emergency_stop":
        return await send_command_to_car(request, {"command": "EMERGENCY_STOP", "source": "web_ui"})

    firmware_mode = mode_mapping.get(req_mode)
    
    if not firmware_mode:
        return {"ok": False, "reason": "unsupported_mode", "mode": mode_request.mode}

    # Safety: Before changing mode, send REMOTE_STOP
    await send_command_to_car(request, {"command": "REMOTE_STOP", "source": "web_ui"})
    
    # Forward mode change to car
    res = await send_command_to_car(request, {"command": "SET_MODE", "mode": firmware_mode, "source": "web_ui"})
    
    if not res.get("ok"):
        return res
        
    return {
        "ok": True, 
        "forwarded": True, 
        "mode": firmware_mode, 
        "note": "waiting_for_car_telemetry_update"
    }


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
