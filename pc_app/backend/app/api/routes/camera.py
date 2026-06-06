from fastapi import APIRouter, Request, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.vision import VisionAnalysisResult
from app.utils.upload_file_utils import read_upload_file_bytes

router = APIRouter(prefix="/api/camera", tags=["camera"])


@router.get("/status")
def camera_status(request: Request) -> dict:
    # Check if any camera is active in the frame hub
    hub = request.app.state.camera_frame_hub
    # Assuming we check for a default or first available camera if ID not provided
    # For now, let's check if any camera has a publisher connected
    active_camera_id = None
    for cid, state in hub._states.items():
        if state.publisher is not None:
            active_camera_id = cid
            break
    
    if active_camera_id:
        status = hub.get_status(active_camera_id)
        return {
            "status": status["status"] if status["status"] == "READY" else "CAMERA_NOT_READY",
            "configured": True,
            "connected": status["publisher_connected"],
            "camera_id": active_camera_id,
            "mode": "WS_PUBLISH",
            "source": f"/ws/cameras/{active_camera_id}/publish",
            "last_seen_at": status["last_seen_at"],
            "last_frame_at": status["last_frame_at"],
            "frame_count": status["frame_count"],
            "latest_frame_size": status["last_frame_size"]
        }

    # Fallback to legacy
    status = request.app.state.camera_service.get_status()
    status["mode"] = "LOCAL_PULL_LEGACY"
    return status

@router.get("/list")
def list_cameras(request: Request) -> list:
    hub = request.app.state.camera_frame_hub
    cameras = []
    for cid, state in hub._states.items():
        status = hub.get_status(cid)
        cameras.append({
            "camera_id": cid,
            "connected": status["publisher_connected"],
            "last_seen_at": status["last_seen_at"],
            "frame_count": status["frame_count"],
            "latest_frame_size": status["last_frame_size"]
        })
    return cameras

from fastapi import HTTPException

@router.post("/analyze-frame", response_model=VisionAnalysisResult)
async def analyze_frame(
    request: Request,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    pipeline = request.app.state.vision_pipeline_service
    
    # Read image bytes
    uploaded_image = await read_upload_file_bytes(image)
    
    # Analyze
    result = await pipeline.analyze_frame(db=db, image_bytes=uploaded_image.content, source="camera_api")
    
    if result.status == "PROVIDER_NOT_READY":
        raise HTTPException(status_code=503, detail="AI provider/model not ready")
        
    return result

@router.post("/detection-frame")
async def detection_frame(
    request: Request,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Shortcut for vision pipeline detection snapshot.
    """
    pipeline = request.app.state.vision_pipeline_service
    
    uploaded_image = await read_upload_file_bytes(image)
    result = await pipeline.analyze_frame(db=db, image_bytes=uploaded_image.content, source="detection_frame")
    
    if result.status == "PROVIDER_NOT_READY":
        raise HTTPException(status_code=503, detail="AI provider/model not ready")
        
    return {
        "status": result.status,
        "message": result.message or f"Detection complete: {result.status}"
    }
