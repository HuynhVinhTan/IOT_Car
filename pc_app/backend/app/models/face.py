import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class FaceTarget(Base):
    __tablename__ = "face_targets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    display_name: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", index=True) # ACTIVE, DISABLED
    notes: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    disabled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    images: Mapped[list["FaceTargetImage"]] = relationship(back_populates="target", cascade="all, delete-orphan")
    embeddings: Mapped[list["FaceEmbedding"]] = relationship(back_populates="target", cascade="all, delete-orphan")

class FaceTargetImage(Base):
    __tablename__ = "face_target_images"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    target_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("face_targets.id", ondelete="CASCADE"), index=True)
    media_asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("media_assets.id"), index=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    target: Mapped["FaceTarget"] = relationship(back_populates="images")
    media_asset: Mapped["MediaAsset"] = relationship(primaryjoin="FaceTargetImage.media_asset_id == MediaAsset.id")

class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    target_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("face_targets.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(50)) # insightface, facenet, etc
    dimension: Mapped[Optional[int]] = mapped_column(nullable=True)
    embedding_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="READY") # READY, NOT_READY, FAILED
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    target: Mapped["FaceTarget"] = relationship(back_populates="embeddings")
