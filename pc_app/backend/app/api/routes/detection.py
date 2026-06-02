from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.mission import DetectionState
from app.services.detection_service import DetectionService

router = APIRouter(prefix="/api/detection", tags=["detection"])

class PersonDetectedRequest(BaseModel):
    confidence: float | None = None
    source: str = "ai"

class MockDetectionRequest(BaseModel):
    object_type: str = "person"
    target_person_id: Optional[str] = None
    confidence: float = 1.0
    detected_segment_id: Optional[str] = None
    message: str = "Mock person found"

@router.get("/events")
async def get_detection_history(request: Request, db: AsyncSession = Depends(get_db)):
    service = request.app.state.detection_service
    events = await service.get_history(db)
    return events

@router.get("/state", response_model=DetectionState)
async def get_detection_state(request: Request):
    service = request.app.state.detection_service
    return service.get_state()

@router.post("/person-detected")
async def person_detected(
    request: Request,
    payload: PersonDetectedRequest, 
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    service = request.app.state.detection_service
    
    event = await service.person_detected(
        db,
        payload.confidence, 
        source=payload.source,
        snapshot_file=image.file if image else None
    )
    
    # Background broadcast
    manager = request.app.state.connection_manager
    await manager.broadcast_json({
        "type": "detection_event",
        "event": "person_detected",
        "source": payload.source,
        "status": service.get_state().status
    })
    return event

@router.post("/person-lost")
async def person_lost(request: Request, db: AsyncSession = Depends(get_db)):
    service = request.app.state.detection_service
    
    event = await service.person_lost(db)
    manager = request.app.state.connection_manager
    await manager.broadcast_json({
        "type": "detection_event",
        "event": "person_lost",
        "status": "NO_PERSON"
    })
    return event

@router.post("/mock-found")
async def mock_found(request: Request, payload: MockDetectionRequest, db: AsyncSession = Depends(get_db)):
    service = request.app.state.detection_service
    
    event = await service.person_detected(
        db,
        payload.confidence, 
        source="mock",
        target_person_id=payload.target_person_id
    )
    return service.get_state()

@router.post("/mock-lost")
async def mock_lost(request: Request, db: AsyncSession = Depends(get_db)):
    service = request.app.state.detection_service
    await service.person_lost(db)
    return service.get_state()

@router.post("/clear")
async def clear_detection(request: Request, db: AsyncSession = Depends(get_db)):
    service = request.app.state.detection_service
    await service.clear_state(db)
    return {"status": "SUCCESS"}
