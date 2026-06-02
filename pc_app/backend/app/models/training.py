import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_name: Mapped[str] = mapped_column(String(100), index=True)
    map_id: Mapped[str] = mapped_column(String(50), default="default_map")
    segment_id: Mapped[str] = mapped_column(String(50), index=True)
    direction: Mapped[str] = mapped_column(String(50), index=True)
    start_node: Mapped[str] = mapped_column(String(20))
    target_node: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(30), default="IDLE", index=True) # RECORDING, STOPPED, EXPORTED
    record_camera: Mapped[bool] = mapped_column(Boolean, default=True)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    output_dataset_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    stopped_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    exported_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    samples: Mapped[list["TrainingSample"]] = relationship(back_populates="session", cascade="all, delete-orphan")

class TrainingSample(Base):
    __tablename__ = "training_samples"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("training_sessions.id", ondelete="CASCADE"), index=True)
    media_asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("media_assets.id"), nullable=True)
    
    timestamp_ms: Mapped[int] = mapped_column(Integer)
    segment_id: Mapped[str] = mapped_column(String(50))
    direction: Mapped[str] = mapped_column(String(50))
    
    # Telemetry snippet
    current_node: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    current_segment_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_node: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    joystick_x: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    joystick_y: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    left_motor_speed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    right_motor_speed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    front_distance_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    left_distance_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    right_distance_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rear_distance_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    forward_unsafe: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    object_found: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # AI Vision Metadata
    distance_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # far, mid, near
    view_angle: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # front, left, right, back
    person_visible: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    face_visible: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    face_quality: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # clear, blurry, too_small
    target_person_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("face_targets.id"), nullable=True)
    bbox_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    session: Mapped["TrainingSession"] = relationship(back_populates="samples")
    media_asset: Mapped[Optional["MediaAsset"]] = relationship(primaryjoin="TrainingSample.media_asset_id == MediaAsset.id")
