from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.face import FaceTarget, FaceTargetImage
from app.repositories.ai_repository import FaceTargetRepository
from app.repositories.base_repository import BaseRepository
from app.services.media.media_asset_service import MediaAssetService
from app.schemas.face import FaceTargetCreate
from app.services.face.face_recognition_service import FaceRecognitionService
from app.models.face import FaceEmbedding
from app.utils.upload_file_utils import UploadedBinary

class FaceRegistryService:
    def __init__(self, db: AsyncSession, recognition_service: FaceRecognitionService):
        self.db = db
        self.repo = FaceTargetRepository(FaceTarget, db)
        self.img_repo = BaseRepository(FaceTargetImage, db)
        self.media_service = MediaAssetService(db)
        self.recognition_service = recognition_service

    async def register_target(self, req: FaceTargetCreate) -> FaceTarget:
        target = FaceTarget(
            display_name=req.display_name,
            notes=req.notes
        )
        return await self.repo.create(target)

    async def list_targets(self) -> List[FaceTarget]:
        return await self.repo.list_all()

    async def get_target(self, target_id: any) -> Optional[FaceTarget]:
        return await self.repo.get_by_id(target_id)

    async def delete_target(self, target_id: any):
        # Soft delete by setting status to DISABLED
        await self.repo.update(target_id, status="DISABLED", disabled_at=datetime.utcnow())

    async def get_status(self) -> Dict[str, Any]:
        targets = await self.repo.list_active()
        return {
            "registered_targets": len(targets),
            "status": "READY" if targets else "EMPTY"
        }

    async def add_target_image(self, target_id: any, uploaded_image: UploadedBinary, is_primary: bool = False):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Adding image to target {target_id}: {uploaded_image.filename}, size={uploaded_image.size}")

        if not self.recognition_service or not self.recognition_service.is_ready():
            raise HTTPException(status_code=503, detail="Face recognition model not ready")

        try:
            asset = await self.media_service.upload_asset(
                image_bytes=uploaded_image.content,
                folder=f"face_targets/{target_id}",
                purpose="face_target",
                filename=uploaded_image.filename
            )
            logger.info(f"Media asset created: {asset.id}, url={asset.secure_url}")
        except Exception as e:
            logger.error(f"Media upload failed: {e}")
            raise HTTPException(status_code=500, detail="Media save failed")

        try:
            embedding = await self.recognition_service.enroll_target(uploaded_image.content)
            if embedding is None:
                raise ValueError("No face detected")
            
            logger.info(f"Embedding generated, dim={len(embedding)}")
            
            target_image = FaceTargetImage(target_id=target_id, media_asset_id=asset.id, is_primary=is_primary)
            self.db.add(target_image)
            
            emb_record = FaceEmbedding(
                target_id=target_id,
                provider="insightface",
                dimension=len(embedding),
                embedding_json={"vector": embedding.tolist()},
                status="READY"
            )
            self.db.add(emb_record)
            await self.db.commit()
            await self.recognition_service.build_cache(self.db)
            
            # Return full info for validation
            return {
                "image_id": target_image.id,
                "media_asset_id": asset.id,
                "embedding_id": emb_record.id
            }
        except ValueError as e:
            await self.db.rollback()
            logger.warning(f"Enrollment validation failed for {uploaded_image.filename}: {e}")
            logger.debug(f"Details: filename={uploaded_image.filename}, content_type={uploaded_image.content_type}, size={uploaded_image.size}, asset_id={asset.id if 'asset' in locals() else None}")
            raise HTTPException(status_code=422, detail="No face detected. Please upload a clear frontal face image.")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Embedding/DB save failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Embedding save failed")
