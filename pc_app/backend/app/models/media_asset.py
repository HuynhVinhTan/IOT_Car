import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(50), default="cloudinary")
    public_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    secure_url: Mapped[str] = mapped_column(String(1024))
    resource_type: Mapped[str] = mapped_column(String(50), default="image")
    folder: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    format: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    purpose: Mapped[str] = mapped_column(String(50), index=True) # training_frame, face_target, etc
    
    # AI Vision Metadata
    distance_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # far, mid, near
    view_angle: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # front, left, right, back
    person_visible: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    face_visible: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    face_quality: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # clear, blurry, too_small
    target_person_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("face_targets.id"), nullable=True)
    bbox_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

class SystemEvent(Base):
    __tablename__ = "system_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    severity: Mapped[str] = mapped_column(String(20), default="info") # info, warning, error
    source: Mapped[str] = mapped_column(String(100))
    message: Mapped[str] = mapped_column(String(1024))
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
