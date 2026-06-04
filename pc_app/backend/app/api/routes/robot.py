from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Literal

router = APIRouter(prefix="/api/robot", tags=["robot"])

class RobotModeUpdate(BaseModel):
    mode: Literal["manual", "autonomous"]

@router.get("/mode")
async def get_mode(request: Request):
    return {"mode": request.app.state.robot_mode_service.get_mode()}

@router.post("/mode")
async def set_mode(request: Request, update: RobotModeUpdate):
    request.app.state.robot_mode_service.set_mode(update.mode)
    return {"status": "success", "mode": update.mode}

@router.post("/control")
async def send_control(request: Request, payload: dict):
    if not request.app.state.settings.enable_robot_control:
        raise HTTPException(status_code=400, detail="Robot control disabled")
    
    result = request.app.state.car_control_service.send_command(payload)
    return result