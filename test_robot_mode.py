import asyncio
from app.services.robot.robot_mode_service import RobotModeService
from app.services.robot.robot_decision_service import RobotDecisionService
from unittest.mock import MagicMock

async def test_manual_mode_blocks_autonomous():
    # Mock dependencies
    mock_car_control = MagicMock()
    mock_settings = MagicMock()
    mock_settings.remote_drive_max_motor_speed = 100
    
    mode_service = RobotModeService()
    decision_service = RobotDecisionService(mock_car_control, mode_service, mock_settings)
    
    # Set to manual
    mode_service.set_mode("manual")
    
    # Try to send autonomous command
    result = await decision_service._send_command_async({"command": "REMOTE_DRIVE", "left_motor_speed": 50, "right_motor_speed": 50})
    
    print(f"Result when manual: {result}")
    assert result["status"] == "IGNORED"
    
    # Try to send emergency stop
    result_stop = await decision_service._send_command_async({"command": "EMERGENCY_STOP"})
    print(f"Result for emergency stop: {result_stop}")
    assert result_stop["status"] != "IGNORED"

if __name__ == "__main__":
    asyncio.run(test_manual_mode_blocks_autonomous())