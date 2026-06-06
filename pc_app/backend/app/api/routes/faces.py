from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.utils.upload_file_utils import read_upload_file_bytes
from app.schemas.face import FaceTarget as FaceTargetSchema, FaceTargetCreate, FaceStatus, FaceVerifyResponse
from app.schemas.vision import FaceRecognitionResult
from app.services.face_registry_service import FaceRegistryService
from app.services.face_recognition_service import FaceRecognitionService

router = APIRouter(prefix="/api/faces", tags=["Face Recognition"])

@router.post("/targets", response_model=FaceTargetSchema)
async def register_target(
    display_name: str = Form(...),
    notes: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    recognition_service = getattr(request.app.state, "face_recognition_service", None)
    service = FaceRegistryService(db, recognition_service)
    req = FaceTargetCreate(display_name=display_name, notes=notes)
    target = await service.register_target(req)
    
    if image:
        try:
            uploaded_image = await read_upload_file_bytes(image)
            await service.add_target_image(target.id, uploaded_image, is_primary=True)
        except Exception:
            await db.delete(target)
            await db.commit()
            raise

    # Fetch final state with eager loading
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.face import FaceTargetImage, FaceEmbedding
    from app.models.media import MediaAsset
    
    await db.refresh(target)
    img_res = await db.execute(
        select(FaceTargetImage)
        .options(selectinload(FaceTargetImage.media_asset))
        .where(FaceTargetImage.target_id == target.id)
    )
    images = img_res.scalars().all()
    
    emb_res = await db.execute(select(FaceEmbedding).where(FaceEmbedding.target_id == target.id))
    embedding = emb_res.scalars().first()
    
    image_paths = [img.media_asset.secure_url or img.media_asset.local_url for img in images if img.media_asset]
    embedding_path = str(embedding.id) if embedding else None
    
    if image and (not image_paths or not embedding_path):
        await db.delete(target)
        await db.commit()
        raise HTTPException(status_code=500, detail="FACE_TARGET_ENROLLMENT_INCOMPLETE")
    
    return FaceTargetSchema(
        target_person_id=str(target.id),
        display_name=target.display_name,
        created_at_ms=int(target.created_at.timestamp() * 1000),
        notes=target.notes,
        image_paths=image_paths,
        embedding_path=embedding_path
    )

@router.get("/targets", response_model=List[FaceTargetSchema])
async def list_targets(db: AsyncSession = Depends(get_db), request: Request = None):
    recognition_service = getattr(request.app.state, "face_recognition_service", None)
    service = FaceRegistryService(db, recognition_service)
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
async def delete_target(target_id: str, db: AsyncSession = Depends(get_db), request: Request = None):
    recognition_service = getattr(request.app.state, "face_recognition_service", None)
    service = FaceRegistryService(db, recognition_service)
    await service.delete_target(target_id)
    return {"status": "SUCCESS"}

@router.get("/status", response_model=FaceStatus)
async def get_face_status(request: Request, db: AsyncSession = Depends(get_db)):
    face_recognition_service = getattr(request.app.state, "face_recognition_service", None)
    service = FaceRegistryService(db, face_recognition_service)
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

@router.post("/targets/{target_id}/activate")
async def activate_target(target_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    face_recognition_service: FaceRecognitionService = request.app.state.face_recognition_service
    if not face_recognition_service:
        raise HTTPException(status_code=503, detail="Face recognition service not initialized")
    
    from app.models.face import FaceTarget
    from sqlalchemy import select, update
    
    # Verify target exists and is active
    result = await db.execute(
        select(FaceTarget).where(FaceTarget.id == target_id, FaceTarget.status == "ACTIVE")
    )
    target = result.scalars().first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found or not active")
    
    # Deactivate all other targets
    await db.execute(
        update(FaceTarget).where(FaceTarget.is_active_target == True).values(is_active_target=False)
    )
    # Activate the selected target
    await db.execute(
        update(FaceTarget).where(FaceTarget.id == target_id).values(is_active_target=True)
    )
    await db.commit()
    
    # Update in-memory
    face_recognition_service.set_active_target(target_id)
    
    return {"status": "SUCCESS", "active_target_id": target_id, "display_name": target.display_name}

@router.get("/active-target")
async def get_active_target(request: Request):
    face_recognition_service: FaceRecognitionService = request.app.state.face_recognition_service
    if not face_recognition_service:
        raise HTTPException(status_code=503, detail="Face recognition service not initialized")
    
    active_target_id = face_recognition_service.active_target_id
    if not active_target_id:
        return {"status": "NO_ACTIVE_TARGET", "active_target_id": None, "message": "No target activated"}
    
    return {"status": "SUCCESS", "active_target_id": str(active_target_id)}

@router.post("/verify", response_model=FaceRecognitionResult)
async def verify_face_direct(
    request: Request,
    file: UploadFile = File(...)
):
    """
    MVP Endpoint: Direct face verification from a frame.
    Requires FaceRecognitionService to be available in app.state.
    """
    face_recognition_service: FaceRecognitionService = request.app.state.face_recognition_service
    if not face_recognition_service:
        raise HTTPException(status_code=503, detail="Face recognition service not initialized")
        
    if not face_recognition_service.is_ready():
        raise HTTPException(status_code=503, detail="Face recognition provider not ready")

    uploaded_image = await read_upload_file_bytes(file)
    result = await face_recognition_service.verify_frame_direct(uploaded_image.content)
    return result
