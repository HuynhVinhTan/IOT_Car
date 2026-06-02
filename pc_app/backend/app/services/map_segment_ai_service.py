import os
import json
from typing import Optional, Dict, Any
from app.schemas.ai import SegmentAIStatus, SegmentPrediction

class MapSegmentAIService:
    def __init__(self, models_path: str = "storage/models/map_segment_classifier"):
        self.models_path = models_path
        self._ensure_dirs()
        self.active_model_id: Optional[str] = None
        self.model_info: Dict[str, Any] = {}
        self._load_active_model()

    def _ensure_dirs(self):
        os.makedirs(self.models_path, exist_ok=True)

    def _load_active_model(self):
        manifest_path = os.path.join(self.models_path, "active_model.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r') as f:
                    self.model_info = json.load(f)
                    self.active_model_id = self.model_info.get("model_id")
            except Exception:
                pass

    def get_status(self) -> SegmentAIStatus:
        if not self.active_model_id:
            return SegmentAIStatus(
                status="NOT_READY",
                model_loaded=False,
                reason="No trained segment classifier model found in storage"
            )
        return SegmentAIStatus(
            status="READY",
            model_loaded=True,
            model_version=self.model_info.get("version", "v1")
        )

    def predict(self, frame_data: Any = None) -> SegmentPrediction:
        if not self.active_model_id:
            return SegmentPrediction(
                segment_id="UNKNOWN",
                direction="UNKNOWN",
                confidence=0.0,
                model_version="NONE",
                status="NOT_READY",
                reason="Model not trained"
            )
        
        # MOCK Prediction logic since we don't have real model loading yet
        # In real case, we would use torch/sklearn here
        return SegmentPrediction(
            segment_id="C_E",
            direction="C_to_E",
            confidence=0.95,
            model_version=self.model_info.get("version", "v1")
        )
