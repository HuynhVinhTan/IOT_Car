import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class MissionRun(Base):
    __tablename__ = "mission_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    mission_type: Mapped[str] = mapped_column(String(50), index=True) # SEARCH, PATROL, etc
    status: Mapped[str] = mapped_column(String(30), default="STARTED", index=True) # STARTED, COMPLETED, FAILED, ABORTED
    start_node: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    target_node: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(nullable=True)
    result_summary: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    
    events: Mapped[list["MissionEvent"]] = relationship(back_populates="mission", cascade="all, delete-orphan")

class MissionEvent(Base):
    __tablename__ = "mission_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    mission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mission_runs.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True) # REACHED_NODE, DETECTION, ERROR, etc
    message: Mapped[str] = mapped_column(String(512))
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    mission: Mapped["MissionRun"] = relationship(back_populates="events")
