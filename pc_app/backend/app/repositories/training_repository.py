from sqlalchemy import select, and_
from app.repositories.base_repository import BaseRepository
from app.models.training import TrainingSession, TrainingSample
from app.models.media_asset import MediaAsset, SystemEvent

class TrainingSessionRepository(BaseRepository[TrainingSession]):
    async def get_active_recording(self) -> TrainingSession | None:
        result = await self.session.execute(
            select(self.model).where(self.model.status == "RECORDING").order_by(self.model.created_at.desc())
        )
        return result.scalar_one_or_none()

class TrainingSampleRepository(BaseRepository[TrainingSample]):
    async def get_by_session(self, session_id: any) -> list[TrainingSample]:
        result = await self.session.execute(
            select(self.model).where(self.model.session_id == session_id).order_by(self.model.timestamp_ms.asc())
        )
        return list(result.scalars().all())

class MediaAssetRepository(BaseRepository[MediaAsset]):
    pass

class SystemEventRepository(BaseRepository[SystemEvent]):
    pass
