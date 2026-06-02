from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.training import TrainingSession
from app.repositories.training_repository import TrainingSessionRepository
from app.schemas.training import TrainingSession as TrainingSessionSchema, TrainingSessionStartRequest

class TrainingSessionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TrainingSessionRepository(TrainingSession, db)

    async def start_session(self, req: TrainingSessionStartRequest) -> TrainingSession:
        # Check if any session is already recording
        active = await self.repo.get_active_recording()
        if active:
            raise ValueError(f"Session {active.id} is already recording")

        session = TrainingSession(
            session_name=req.session_name,
            map_id=req.map_id,
            segment_id=req.segment_id,
            direction=req.direction,
            start_node=req.start_node,
            target_node=req.target_node,
            record_camera=req.record_camera,
            status="RECORDING",
            notes=req.notes
        )

        return await self.repo.create(session)

    async def stop_session(self) -> Optional[TrainingSession]:
        active = await self.repo.get_active_recording()
        if not active:
            return None

        return await self.repo.update(active.id, status="STOPPED", stopped_at=datetime.utcnow())

    async def get_current_session(self) -> Optional[TrainingSession]:
        return await self.repo.get_active_recording()

    async def list_sessions(self) -> List[TrainingSession]:
        return await self.repo.list_all()

    async def get_session(self, session_id: str) -> Optional[TrainingSession]:
        return await self.repo.get_by_id(session_id)

    async def update_sample_count(self, session_id: any, count: int):
        await self.repo.update(session_id, sample_count=count)
