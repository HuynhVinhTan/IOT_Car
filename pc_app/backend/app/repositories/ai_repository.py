from sqlalchemy import select
from app.repositories.base_repository import BaseRepository
from app.models.face import FaceTarget, FaceTargetImage, FaceEmbedding
from app.models.detection import DetectionEvent, ModelVersion

class FaceTargetRepository(BaseRepository[FaceTarget]):
    async def list_active(self) -> list[FaceTarget]:
        result = await self.session.execute(
            select(self.model).where(self.model.status == "ACTIVE")
        )
        return list(result.scalars().all())

class DetectionEventRepository(BaseRepository[DetectionEvent]):
    async def get_recent(self, limit: int = 50) -> list[DetectionEvent]:
        result = await self.session.execute(
            select(self.model).order_by(self.model.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

class ModelVersionRepository(BaseRepository[ModelVersion]):
    async def get_active_by_type(self, model_type: str) -> ModelVersion | None:
        result = await self.session.execute(
            select(self.model).where(
                self.model.model_type == model_type,
                self.model.is_active == True,
                self.model.status == "READY"
            ).order_by(self.model.created_at.desc())
        )
        return result.scalar_one_or_none()
