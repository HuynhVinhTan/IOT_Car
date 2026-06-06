import unittest
from unittest.mock import MagicMock

from app.services.robot.car_control_service import CarControlService
from app.services.robot.joystick_service import JoystickService

class TestJoystickFlow(unittest.TestCase):
    def setUp(self):
        # 1. Giả lập (Mock) các Dependency cho CarControlService
        self.mock_car_serial_client = MagicMock()
        self.mock_telemetry_service = MagicMock()
        self.mock_safety_gate_service = MagicMock()
        self.mock_settings = MagicMock()
        
        # Cấu hình tốc độ tối đa là 255
        self.mock_settings.remote_drive_max_motor_speed = 255
        
        # Giả lập xe đang ở chế độ MANUAL_REMOTE và không có lỗi khẩn cấp
        self.mock_telemetry_service.latest_car_telemetry = {
            "mode": "MANUAL_REMOTE", 
            "emergency_reason": ""
        }
        
        # Giả lập Cổng an toàn (Safety Gate) luôn cho phép gửi lệnh đi
        self.mock_safety_gate_service.evaluate_command.return_value = {"allowed": True}
        
        self.car_control_service = CarControlService(
            car_serial_client=self.mock_car_serial_client,
            telemetry_service=self.mock_telemetry_service,
            safety_gate_service=self.mock_safety_gate_service,
            settings=self.mock_settings
        )
        
        # Dùng một list để "hứng" lại các lệnh chuẩn bị gửi ra WebSocket
        self.sent_payloads = []
        def mock_ws_callback(payload):
            self.sent_payloads.append(payload)
            
        self.car_control_service.set_command_callback(mock_ws_callback)

        # 2. Giả lập (Mock) các Dependency cho JoystickService
        self.mock_joystick_serial_client = MagicMock()
        self.mock_remote_control_service = MagicMock()
        self.mock_route_segment_service = MagicMock()

        self.joystick_service = JoystickService(
            telemetry_service=self.mock_telemetry_service,
            car_control_service=self.car_control_service,
            joystick_serial_client=self.mock_joystick_serial_client,
            remote_control_service=self.mock_remote_control_service,
            route_segment_service=self.mock_route_segment_service
        )

    def test_forward_button_press(self):
        """Kiểm tra khi bấm Nút TỚI (Forward), lệnh REMOTE_DRIVE có phát ra đúng không"""
        # Giả lập mạch Joystick gửi JSON khi nhấn Forward (trục Y max = 1.0, X = 0.0)
        joystick_msg = {
            "type": "joystick_telemetry",
            "deadzone_applied": False,
            "normalized_x": 0.0,
            "normalized_y": 1.0
        }
        
        # Backend nhận tín hiệu
        self.joystick_service.handle_joystick_message(joystick_msg)
        
        # Xác minh: Phải có đúng 1 lệnh được nạp vào đường truyền WebSocket
        self.assertEqual(len(self.sent_payloads), 1)
        payload = self.sent_payloads[0]
        
        # Xác minh nội dung lệnh
        self.assertEqual(payload["command"], "REMOTE_DRIVE")
        self.assertEqual(payload["left_motor_speed"], 255)
        self.assertEqual(payload["right_motor_speed"], 255)

    def test_stop_button_release(self):
        """Kiểm tra khi nhả tay (Thả hết 4 nút), lệnh REMOTE_STOP có phát ra không"""
        # Giả lập mạch Joystick gửi JSON khi nhả nút (deadzone_applied = True)
        joystick_msg = {
            "type": "joystick_telemetry",
            "deadzone_applied": True,
            "normalized_x": 0.0,
            "normalized_y": 0.0
        }
        
        # Backend nhận tín hiệu
        self.joystick_service.handle_joystick_message(joystick_msg)
        
        # Xác minh
        self.assertEqual(len(self.sent_payloads), 1)
        payload = self.sent_payloads[0]
        
        self.assertEqual(payload["command"], "REMOTE_STOP")

if __name__ == '__main__':
    unittest.main()
