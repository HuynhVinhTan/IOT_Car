from app.core.database import Base

from app.models.media_asset import MediaAsset, SystemEvent
from app.models.training import TrainingSession, TrainingSample
from app.models.face import FaceTarget, FaceTargetImage, FaceEmbedding
from app.models.detection import DetectionEvent, ModelVersion

# For Alembic or manual creation
__all__ = [
    "MediaAsset",
    "SystemEvent",
    "TrainingSession",
    "TrainingSample",
    "FaceTarget",
    "FaceTargetImage",
    "FaceEmbedding",
    "DetectionEvent",
    "ModelVersion",
]
