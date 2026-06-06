from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.media_asset import MediaAsset
from app.repositories.training_repository import MediaAssetRepository
from app.services.media.cloudinary_media_service import CloudinaryMediaService, MediaUploadResult

class MediaAssetService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MediaAssetRepository(MediaAsset, db)
        self.cloud_service = CloudinaryMediaService()

    async def upload_asset(self, image_bytes: bytes, folder: str, purpose: str, filename: Optional[str] = None) -> MediaAsset:
        # 1. Upload to Cloud/Local
        result: MediaUploadResult = await self.cloud_service.upload_image(image_bytes, folder, filename)
        
        # 2. Record in DB
        asset = MediaAsset(
            provider=result.provider,
            public_id=result.public_id,
            secure_url=result.secure_url,
            resource_type=result.resource_type,
            folder=result.folder,
            format=result.format,
            bytes=result.bytes,
            width=result.width,
            height=result.height,
            original_filename=result.original_filename,
            purpose=purpose
        )
        
        return await self.repo.create(asset)

    async def get_asset(self, asset_id: any) -> Optional[MediaAsset]:
        return await self.repo.get_by_id(asset_id)

    async def delete_asset(self, asset_id: any) -> bool:
        asset = await self.get_asset(asset_id)
        if not asset:
            return False
            
        if asset.provider == "cloudinary" and asset.public_id:
            await self.cloud_service.delete_asset(asset.public_id)
            
        return await self.repo.delete(asset_id)
