from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.face import FaceTarget, FaceTargetImage
from app.repositories.ai_repository import FaceTargetRepository
from app.repositories.base_repository import BaseRepository
from app.services.media_asset_service import MediaAssetService
from app.schemas.face import FaceTargetCreate

class FaceRegistryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = FaceTargetRepository(FaceTarget, db)
        self.img_repo = BaseRepository(FaceTargetImage, db)
        self.media_service = MediaAssetService(db)

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

    async def add_target_image(self, target_id: any, file: Any, is_primary: bool = False):
        asset = await self.media_service.upload_asset(
            file=file,
            folder=f"face_targets/{target_id}",
            purpose="face_target"
        )
        
        target_image = FaceTargetImage(
            target_id=target_id,
            media_asset_id=asset.id,
            is_primary=is_primary
        )
        return await self.img_repo.create(target_image)
