from fastapi import APIRouter, Request, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.vision import VisionAnalysisResult

router = APIRouter(prefix="/api/camera", tags=["camera"])


@router.get("/status")
def camera_status(request: Request) -> dict:
    status = request.app.state.camera_service.get_status()
    status["mode"] = "LOCAL_PULL_LEGACY"
    status["message"] = (
        f"{status.get('message', '')}. Deploy-ready live camera uses "
        "/ws/cameras/{camera_id}/publish and /ws/cameras/{camera_id}/view."
    )
    return status

@router.post("/analyze-frame", response_model=VisionAnalysisResult)
async def analyze_frame(
    request: Request,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    pipeline = request.app.state.vision_pipeline_service
    
    # Read image bytes
    image_bytes = await image.read()
    
    # Analyze
    result = await pipeline.analyze_frame(db=db, image_bytes=image_bytes, source="camera_api")
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
    
    image_bytes = await image.read()
    result = await pipeline.analyze_frame(db=db, image_bytes=image_bytes, source="detection_frame")
    
    return {
        "status": result.status,
        "message": result.message or f"Detection complete: {result.status}"
    }
