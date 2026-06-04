from typing import Any, Optional
from starlette.concurrency import run_in_threadpool
from app.services.robot.car_control_service import CarControlService
from app.schemas.vision import VisionAnalysisResult
from app.core.config import Settings

class RobotDecisionService:
    def __init__(
        self,
        car_control_service: CarControlService,
        settings: Settings
    ):
        self._car_control_service = car_control_service
        self._settings = settings
        self.follow_enabled = False
        self.target_person_id: Optional[str] = None

    def set_follow_enabled(self, enabled: bool, target_id: Optional[str] = None):
        self.follow_enabled = enabled
        self.target_person_id = target_id
        if not enabled:
            self._car_control_service.send_command({"command": "REMOTE_STOP"})

    async def process_vision_result(self, result: VisionAnalysisResult):
        if not self.follow_enabled:
            return

        # If we are in "Follow Person" mode
        if result.status in ["TARGET_FOUND", "PERSON_CANDIDATE"]:
            # Find the best candidate (usually the one vision_pipeline picked)
            # For MVP, let's assume we follow the largest person if target_person_id matches or not set
            candidate = None
            if result.face_result and self.target_person_id and str(result.face_result.target_person_id) == self.target_person_id:
                # Specific target found
                candidate = next((c for c in result.person_candidates if c.confidence > 0.5), None) 
            elif not self.target_person_id:
                # Follow any person
                candidate = max(result.person_candidates, key=lambda c: (c.bbox[2]-c.bbox[0]) * (c.bbox[3]-c.bbox[1]))
            
            if candidate:
                await self._execute_follow_logic(candidate.bbox)
            else:
                await self._send_command_async({"command": "REMOTE_STOP"})
        else:
            # Person lost
            await self._send_command_async({"command": "REMOTE_STOP"})

    async def _execute_follow_logic(self, bbox: list[float]):
        """
        bbox: [x1, y1, x2, y2] normalized 0.0 to 1.0
        """
        x_center = (bbox[0] + bbox[2]) / 2.0
        width = bbox[2] - bbox[0]
        
        # 1. Steering (Yaw)
        # x_center: 0.0 (left) to 1.0 (right). Center is 0.5.
        error_x = x_center - 0.5
        steer_gain = 1.5
        steer = error_x * steer_gain # -0.75 to 0.75
        
        # 2. Speed (Distance)
        # width: 0.0 (far) to 1.0 (very close). 
        # Target width: 0.3 (about 1.5 meters away?)
        target_width = 0.3
        error_dist = target_width - width
        speed_gain = 2.0
        speed = error_dist * speed_gain # Positive if too far, negative if too close
        
        # Clamp speed/steer
        speed = max(-0.5, min(0.5, speed))
        steer = max(-0.5, min(0.5, steer))
        
        # Convert to motor speeds
        # Differential drive:
        left_speed = speed + steer
        right_speed = speed - steer
        
        # Scale to max motor speed
        max_motor_speed = self._settings.remote_drive_max_motor_speed
        
        l_pwm = int(left_speed * max_motor_speed)
        r_pwm = int(right_speed * max_motor_speed)
        
        # Clamp to valid PWM range
        l_pwm = max(-max_motor_speed, min(max_motor_speed, l_pwm))
        r_pwm = max(-max_motor_speed, min(max_motor_speed, r_pwm))
        
        if abs(l_pwm) < 40 and abs(r_pwm) < 40:
             await self._send_command_async({"command": "REMOTE_STOP"})
        else:
             await self._send_command_async({
                 "command": "REMOTE_DRIVE",
                 "left_motor_speed": l_pwm,
                 "right_motor_speed": r_pwm
             })

    async def _send_command_async(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await run_in_threadpool(self._car_control_service.send_command, payload)
