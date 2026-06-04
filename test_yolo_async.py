import asyncio
from app.services.vision.person_detection_service import PersonDetectionService
from app.core.config import settings

async def test_yolo():
    # Tạm thời set enable_person_detection = False để test load model
    service = PersonDetectionService()
    print(f"Service ready: {service.is_ready()}")
    
    # Nếu model chưa load, thử init
    if not service.is_ready():
        service._init_yolo()
        
    if service.is_ready():
        # Giả lập gọi detect (cần file ảnh thật hoặc bytes)
        # Ở đây chỉ test việc gọi hàm async
        print("YOLO ready, skipping inference test due to missing image")
    else:
        print("YOLO not ready")

if __name__ == "__main__":
    asyncio.run(test_yolo())