from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.face import FaceTarget as FaceTargetSchema, FaceTargetCreate, FaceStatus, FaceVerifyResponse
from app.services.face_registry_service import FaceRegistryService

router = APIRouter(prefix="/api/faces", tags=["Face Recognition"])

@router.post("/targets", response_model=FaceTargetSchema)
async def register_target(
    display_name: str = Form(...),
    notes: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    service = FaceRegistryService(db)
    req = FaceTargetCreate(display_name=display_name, notes=notes)
    target = await service.register_target(req)
    
    if image:
        await service.add_target_image(target.id, image.file, is_primary=True)
    
    return FaceTargetSchema(
        target_person_id=str(target.id),
        display_name=target.display_name,
        created_at_ms=int(target.created_at.timestamp() * 1000),
        notes=target.notes
    )

@router.get("/targets", response_model=List[FaceTargetSchema])
async def list_targets(db: AsyncSession = Depends(get_db)):
    service = FaceRegistryService(db)
    targets = await service.list_targets()
    return [
        FaceTargetSchema(
            target_person_id=str(t.id),
            display_name=t.display_name,
            created_at_ms=int(t.created_at.timestamp() * 1000),
            notes=t.notes
        ) for t in targets if t.status == "ACTIVE"
    ]

@router.delete("/targets/{target_id}")
async def delete_target(target_id: str, db: AsyncSession = Depends(get_db)):
    service = FaceRegistryService(db)
    await service.delete_target(target_id)
    return {"status": "SUCCESS"}

@router.get("/status", response_model=FaceStatus)
async def get_face_status(request: Request, db: AsyncSession = Depends(get_db)):
    face_recognition_service = getattr(request.app.state, "face_recognition_service", None)
    service = FaceRegistryService(db)
    reg_status = await service.get_status()
    provider_ready = (
        bool(face_recognition_service.is_ready())
        if face_recognition_service is not None
        else False
    )
    
    return FaceStatus(
        status=reg_status["status"] if provider_ready else "PROVIDER_NOT_READY",
        registered_targets=reg_status["registered_targets"],
        embedding_provider_ready=provider_ready,
        message=(
            "Face recognition provider is ready"
            if provider_ready
            else "Face recognition provider is not initialized"
        )
    )
