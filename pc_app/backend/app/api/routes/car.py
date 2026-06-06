from fastapi import APIRouter, HTTPException, Request

import json
import pathlib

from pydantic import BaseModel, Field

from app.schemas.car_command import CarCommand, ModeRequest

router = APIRouter(prefix="/api/car", tags=["car"])


class LoadMapRequest(BaseModel):
    map_id: str = Field(min_length=1)
    start_node_id: str = Field(min_length=1)


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


@router.post("/load-map")
async def load_map(request: Request, body: LoadMapRequest) -> dict:

    """Load a stored map from disk and forward it to the car firmware.
    
    Payload is minimized for firmware: nodes include id/x/y; edges include from/to.
    """
    
    

    base_dir = pathlib.Path(__file__).parent.parent.parent.parent
    data_dir = base_dir / "data"
    maps_dir = data_dir / "maps"

    map_path = maps_dir / f"{body.map_id}.json"
    if not map_path.exists():
        raise HTTPException(status_code=404, detail="Map not found")

    try:
        with open(map_path, "r", encoding="utf-8") as f:
            raw_map = json.load(f)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read map: {exc}")

    nodes = raw_map.get("nodes")
    edges = raw_map.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise HTTPException(status_code=400, detail="Invalid map schema (nodes/edges)")

    node_ids: set[str] = set()
    fw_nodes: list[dict] = []
    for n in nodes:
        if not isinstance(n, dict):
            continue
        node_id = n.get("id")
        if not node_id:
            continue
        try:
            x = float(n.get("x", 0.0))
            y = float(n.get("y", 0.0))
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid node coordinates for {node_id}")
        node_ids.add(str(node_id))
        fw_nodes.append({"id": str(node_id), "x": x, "y": y})

    if body.start_node_id not in node_ids:
        raise HTTPException(status_code=400, detail="start_node_id not found in map nodes")

    fw_edges: list[dict] = []
    for e in edges:
        if not isinstance(e, dict):
            continue
        # Web UI uses from/to; older schemas may use source/target
        from_id = e.get("from") or e.get("source")
        to_id = e.get("to") or e.get("target")
        if not from_id or not to_id:
            continue
        from_id = str(from_id)
        to_id = str(to_id)
        if from_id not in node_ids or to_id not in node_ids:
            # Skip edges that reference missing nodes
            continue
        fw_edges.append({"from": from_id, "to": to_id})

    firmware_payload = {
        "command": "LOAD_MAP",
        "map_id": body.map_id,
        "start_node_id": body.start_node_id,
        "nodes": fw_nodes,
        "edges": fw_edges,
        "source": "backend_api",
    }

    return await send_command_to_car(request, firmware_payload)

@router.post("/command")
async def send_command(request: Request, command: CarCommand) -> dict:
    from app.core.loggers import logger
    
    telemetry_service = request.app.state.telemetry_service
    settings = request.app.state.settings
    
    # Get car info for logging
    latest = telemetry_service.latest_car_telemetry
    mode = latest.get("mode") if latest else "IDLE"
    car_id = getattr(settings, "car_controller_id", "car_controller_01")
    connected = telemetry_service.car_connected(settings.car_offline_timeout_seconds)
    
    payload = command.to_payload()
    cmd_type = payload.get("command")
    
    # Log the request
    logger.info(
        "remote control request: command=%s car_id=%s mode=%s connected=%s",
        cmd_type,
        car_id,
        mode,
        connected,
    )
    
    # Check if car is connected
    if not connected:
        return {
            "ok": False,
            "reason": "car_controller_not_connected",
            "command": cmd_type,
            "car_id": car_id,
            "sent_to_car": False
        }
         
    # Check mode (only for non-stop commands)
    if cmd_type != "REMOTE_STOP" and mode not in ["MANUAL_REMOTE", "SERVER_CONTROL"]:
        return {
            "ok": False, 
            "reason": "car_not_in_server_control_mode",
            "current_mode": mode,
            "command": cmd_type,
            "car_id": car_id,
            "sent_to_car": False
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
        
    result = await send_command_to_car(request, firmware_payload)
    
    # Format response to match requirements
    if result.get("ok"):
        return {
            "ok": True,
            "command": cmd_type,
            "car_id": car_id,
            "sent_to_car": True
        }
    else:
        return {
            "ok": False,
            "reason": result.get("reason", "unknown_error"),
            "command": cmd_type,
            "car_id": car_id,
            "sent_to_car": False
        }


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
