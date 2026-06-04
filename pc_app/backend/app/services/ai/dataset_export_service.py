import os
import json
import csv
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.training_repository import TrainingSessionRepository, TrainingSampleRepository
from app.models.training import TrainingSession, TrainingSample

class DatasetExportService:
    def __init__(self, db: AsyncSession, export_base_path: str = "dataset/map_segments"):
        self.db = db
        self.export_base_path = export_base_path
        self.session_repo = TrainingSessionRepository(TrainingSession, db)
        self.sample_repo = TrainingSampleRepository(TrainingSample, db)

    async def export_session(self, session_id: str) -> Dict[str, Any]:
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            return {"status": "ERROR", "message": f"Session {session_id} not found"}

        samples = await self.sample_repo.get_by_session(session_id)
        if not samples:
            return {"status": "ERROR", "message": "No samples found in session"}

        target_path = os.path.join(self.export_base_path, session.segment_id, session.direction)
        os.makedirs(target_path, exist_ok=True)

        manifest_file = os.path.join(target_path, f"manifest_{session_id}.json")
        csv_file = os.path.join(target_path, f"manifest_{session_id}.csv")

        exported_data = []
        for s in samples:
            media_item = s.media_asset
            
            sample_dict = {
                "sample_id": str(s.id),
                "timestamp_ms": s.timestamp_ms,
                "segment_id": s.segment_id,
                "direction": s.direction,
                "media_url": media_item.secure_url if media_item else None,
                "media_provider": media_item.provider if media_item else None,
                "joystick_x": s.joystick_x,
                "joystick_y": s.joystick_y,
                "left_motor_speed": s.left_motor_speed,
                "right_motor_speed": s.right_motor_speed,
                "front_distance_cm": s.front_distance_cm,
                "left_distance_cm": s.left_distance_cm,
                "right_distance_cm": s.right_distance_cm,
                "rear_distance_cm": s.rear_distance_cm,
                "forward_unsafe": s.forward_unsafe,
                "object_found": s.object_found
            }
            exported_data.append(sample_dict)

        with open(manifest_file, 'w') as f:
            json.dump(exported_data, f, indent=2)

        if exported_data:
            keys = exported_data[0].keys()
            with open(csv_file, 'w', newline='') as f:
                dict_writer = csv.DictWriter(f, keys)
                dict_writer.writeheader()
                dict_writer.writerows(exported_data)

        await self.session_repo.update(session_id, 
            status="EXPORTED", 
            exported_at=datetime.utcnow(),
            output_dataset_path=target_path
        )

        return {
            "status": "SUCCESS",
            "session_id": session_id,
            "export_path": target_path,
            "samples_exported": len(samples),
            "manifest_url": manifest_file,
            "message": f"Exported {len(samples)} samples to {target_path}"
        }
