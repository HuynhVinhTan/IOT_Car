import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class DetectionEvent(Base):
    __tablename__ = "detection_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(50), index=True) # PERSON_FOUND, OBJECT_LOST, etc
    target_person_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("face_targets.id"), nullable=True, index=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    detected_node: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    detected_segment_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    snapshot_asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("media_assets.id"), nullable=True)
    person_bbox_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    face_bbox_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="camera_ai", index=True) # mock, person_detection, face_recognition, camera_pipeline
    message: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    snapshot: Mapped[Optional["MediaAsset"]] = relationship(primaryjoin="DetectionEvent.snapshot_asset_id == MediaAsset.id")
    target_person: Mapped[Optional["FaceTarget"]] = relationship()

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    model_type: Mapped[str] = mapped_column(String(100), index=True) # map_segment_classifier, face_recognition
    version: Mapped[str] = mapped_column(String(20))
    model_path: Mapped[str] = mapped_column(String(1024))
    labels_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    metrics_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="READY", index=True) # READY, TRAINING, FAILED
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
