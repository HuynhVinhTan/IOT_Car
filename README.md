# Smart Car IoT — Autonomous Robot Platform

Smart Car IoT là hệ thống xe robot thông minh sử dụng ESP32, ESP32-CAM, FastAPI Backend và Web Dashboard để hỗ trợ điều khiển từ xa, truyền dữ liệu cảm biến, xử lý hình ảnh, nhận diện khuôn mặt và vận hành robot ở chế độ bán tự động hoặc tự hành.

Dự án được thiết kế theo hướng mô-đun, dễ mở rộng, phù hợp cho bài toán IoT, robotics, computer vision và điều khiển thiết bị thời gian thực.

---

## 1. Tổng quan hệ thống

Hệ thống bao gồm các thành phần chính:

| Thành phần            | Vai trò                                                                    |
| --------------------- | -------------------------------------------------------------------------- |
| ESP32 Car Controller  | Điều khiển động cơ, đọc cảm biến siêu âm, cảm biến tốc độ và gửi telemetry |
| ESP32-CAM Camera Node | Gửi hình ảnh camera về backend qua WebSocket                               |
| FastAPI Backend       | Trung tâm xử lý API, WebSocket, telemetry, robot mode, AI pipeline         |
| Web Dashboard         | Giao diện giám sát trạng thái xe, camera, điều khiển và cấu hình chế độ    |
| AI Vision Pipeline    | Nhận diện khuôn mặt, phát hiện người, hỗ trợ điều hướng tự hành            |
| Cloud Storage         | Lưu ảnh/video nếu cần, không lưu trực tiếp media vào database              |

---

## 2. Tính năng chính

### Điều khiển robot

* Điều khiển xe qua API hoặc Web Dashboard.
* Hỗ trợ nhiều chế độ vận hành.
* Gửi lệnh di chuyển: tiến, lùi, trái, phải, dừng.
* Thiết kế an toàn: motor mặc định dừng sau khi boot.

### Giám sát thời gian thực

* Nhận telemetry từ ESP32 qua WebSocket.
* Theo dõi trạng thái kết nối của xe.
* Hiển thị dữ liệu cảm biến siêu âm.
* Hỗ trợ truyền frame camera từ ESP32-CAM.

### Xử lý hình ảnh và AI

* Đăng ký khuôn mặt mục tiêu.
* Xác minh khuôn mặt từ ảnh hoặc frame camera.
* Hỗ trợ pipeline nhận diện người bằng YOLO.
* Hỗ trợ tính toán hướng di chuyển dựa trên vị trí bounding box.

### Kiến trúc mở rộng

* Tách biệt firmware, backend và frontend.
* Backend dùng service layer rõ ràng.
* Dễ mở rộng thêm cảm biến, thuật toán AI hoặc chế độ điều khiển mới.
* Phù hợp triển khai local hoặc production.

---

## 3. Kiến trúc tổng thể

```text
+------------------+        WebSocket/API        +----------------------+
|  ESP32 Controller|  <------------------------>  |    FastAPI Backend   |
|  Motor + Sensors |                              |  Robot Core Services |
+------------------+                              +----------+-----------+
                                                              |
                                                              |
+------------------+        WebSocket Camera       +----------v-----------+
|    ESP32-CAM     |  -------------------------->  |  Vision Pipeline     |
|  Camera Streaming|                              | Face / Person Detect |
+------------------+                              +----------+-----------+
                                                              |
                                                              |
                                                   +----------v-----------+
                                                   |    Web Dashboard     |
                                                   | Control / Monitor UI |
                                                   +----------------------+
```

---

## 4. Công nghệ sử dụng

### Firmware

* ESP32
* ESP32-CAM
* PlatformIO
* Arduino Framework
* WebSocket Client
* Ultrasonic Sensor
* IR Speed Sensor
* L298N Motor Driver

### Backend

* Python
* FastAPI
* Uvicorn
* WebSocket
* Pydantic
* OpenCV
* InsightFace / ArcFace
* YOLO Object Detection
* AsyncIO

### Frontend

* Web Dashboard
* Vite
* JavaScript / TypeScript
* REST API
* WebSocket Client

### Storage / Deployment

* Cloudinary cho media storage
* Railway hoặc môi trường cloud tương đương cho backend production
* Local development qua Uvicorn và PlatformIO

---

## 5. Cấu trúc thư mục đề xuất

```text
smart_car/
├── firmware/
│   ├── car_controller_esp32/
│   │   ├── src/
│   │   ├── include/
│   │   ├── platformio.ini
│   │   └── README.md
│   │
│   └── camera_node_esp32_cam/
│       ├── src/
│       ├── include/
│       ├── platformio.ini
│       └── README.md
│
├── pc_app/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── services/
│   │   │   ├── schemas/
│   │   │   └── main.py
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   └── frontend/
│       ├── src/
│       ├── package.json
│       └── README.md
│
├── docs/
│   ├── hardware.md
│   ├── api.md
│   └── deployment.md
│
└── README.md
```

---

## 6. Sơ đồ chân phần cứng

### Cảm biến siêu âm

| Vị trí   | TRIG | ECHO |
| -------- | ---: | ---: |
| Bên phải |  D23 |  D35 |
| Bên trái |  D22 |  D34 |

> Lưu ý: GPIO34 và GPIO35 là chân input-only, phù hợp để đọc tín hiệu ECHO.

### Driver động cơ L298N

| L298N | ESP32 |
| ----- | ----: |
| ENA   |    D2 |
| ENB   |   D19 |
| IN1   |   D32 |
| IN2   |   D33 |
| IN3   |   D25 |
| IN4   |   D26 |

### Cảm biến tốc độ IR FC-03

| Vị trí   | ESP32 |
| -------- | ----: |
| Bên phải |   D13 |
| Bên trái |   D27 |

---

## 7. Lưu ý an toàn phần cứng

Trước khi cấp nguồn riêng cho motor hoặc L298N motor power, cần đảm bảo:

* ESP32 boot thành công.
* Serial Monitor đọc log bình thường.
* Sensor ultrasonic hoạt động ổn định.
* Motor mặc định ở trạng thái STOP sau khi boot.
* Không cấp nguồn motor khi firmware chưa được kiểm tra.
* Không nối trực tiếp chân ECHO 5V của HC-SR04 vào ESP32.

Nếu dùng HC-SR04 loại xuất tín hiệu ECHO 5V, bắt buộc dùng mạch chia áp hoặc level shifter để hạ tín hiệu xuống 3.3V trước khi đưa vào ESP32.

---

## 8. Cài đặt môi trường

### Yêu cầu chung

* Python 3.10+
* Node.js 18+
* PlatformIO
* Git
* ESP32 USB Driver, ví dụ CH340
* Webcam hoặc ESP32-CAM
* Board ESP32 / ESP32-CAM

---

## 9. Chạy Backend

Di chuyển vào thư mục backend:

```bash
cd smart_car/pc_app/backend
```

Tạo môi trường ảo:

```bash
python -m venv .venv
```

Kích hoạt môi trường ảo trên Windows:

```bash
.venv\Scripts\activate
```

Cài dependencies:

```bash
pip install -r requirements.txt
```

Chạy backend:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Kiểm tra trạng thái backend:

```bash
curl http://localhost:8000/api/car/status
```

Kết quả mong đợi:

```json
{
  "connected": false,
  "telemetry": null
}
```

---

## 10. Chạy Frontend

Di chuyển vào thư mục frontend:

```bash
cd smart_car/pc_app/frontend
```

Cài dependencies:

```bash
npm install
```

Chạy development server:

```bash
npm run dev
```

Mặc định frontend thường chạy tại:

```text
http://localhost:5173
```

---

## 11. Build và nạp firmware ESP32 Car Controller

Di chuyển vào thư mục firmware:

```bash
cd smart_car/firmware/car_controller_esp32
```

Build firmware:

```bash
python -m platformio run
```

Upload firmware:

```bash
python -m platformio run --target upload
```

Mở Serial Monitor:

```bash
python -m platformio device monitor --port COM4 -b 115200
```

> Nếu máy tính nhận ESP32 ở cổng khác, thay `COM4` bằng cổng thực tế.

---

## 12. Build và nạp firmware ESP32-CAM

Di chuyển vào thư mục ESP32-CAM:

```bash
cd smart_car/firmware/camera_node_esp32_cam
```

Build firmware:

```bash
python -m platformio run
```

Upload firmware:

```bash
python -m platformio run --target upload
```

Mở Serial Monitor:

```bash
python -m platformio device monitor --port COM4 -b 115200
```

---

## 13. Các chế độ vận hành

### FACE_VERIFICATION_MVP

Chế độ kiểm thử nhận diện khuôn mặt tối thiểu.

Đặc điểm:

* Không yêu cầu robot thật.
* Không cần kết nối serial.
* Không cần YOLO.
* Dùng để enroll và verify khuôn mặt.
* Phù hợp kiểm thử AI face recognition độc lập.

### ROBOT_AUTONOMOUS_PIPELINE

Chế độ robot tự hành.

Đặc điểm:

* Kết nối robot controller.
* Nhận dữ liệu camera.
* Chạy vision pipeline.
* Tính toán quyết định điều hướng.
* Có thể kết hợp phát hiện người và xác minh khuôn mặt.

---

## 14. API chính

### Kiểm tra trạng thái xe

```http
GET /api/car/status
```

### Đổi chế độ robot

```http
POST /api/robot/mode
Content-Type: application/json

{
  "mode": "ROBOT_AUTONOMOUS_PIPELINE"
}
```

### Gửi lệnh điều khiển robot

```http
POST /api/robot/control
Content-Type: application/json

{
  "command": "forward"
}
```

### Đăng ký khuôn mặt mục tiêu

```http
POST /api/faces/targets
Content-Type: multipart/form-data
```

### Xác minh khuôn mặt

```http
POST /api/faces/verify
Content-Type: multipart/form-data
```

---

## 15. WebSocket endpoints

### ESP32 Controller gửi telemetry

```text
/ws/car
```

Dùng để ESP32 gửi dữ liệu trạng thái xe, cảm biến và kết nối về backend.

### ESP32-CAM gửi frame camera

```text
/ws/camera/publish
```

Dùng để ESP32-CAM gửi frame hình ảnh về backend.

### Backend gửi telemetry cho frontend

```text
/ws/telemetry
```

Dùng để frontend nhận dữ liệu realtime từ backend.

---

## 16. Biến môi trường đề xuất

Tạo file `.env` trong thư mục backend:

```env
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

ENABLE_PERSON_DETECTION=false
ENABLE_FACE_RECOGNITION=true
ENABLE_ROBOT_CONTROL=true

CAR_ID=car_controller_01
```

Không commit file `.env` lên Git. Chỉ commit `.env.example`.

---

## 17. Quy trình kiểm thử đề xuất

### Kiểm thử backend

```bash
python -m pytest
```

### Kiểm tra syntax Python

```bash
python -m compileall app
```

### Kiểm thử API thủ công

```bash
curl http://localhost:8000/api/car/status
```

### Kiểm thử firmware

```bash
python -m platformio run
```

### Kiểm tra serial

```bash
python -m platformio device monitor --port COM4 -b 115200
```

---

## 18. Checklist vận hành an toàn

Trước khi chạy robot thực tế:

* [ ] ESP32 boot ổn định.
* [ ] Serial Monitor có log.
* [ ] Backend chạy thành công.
* [ ] API `/api/car/status` phản hồi đúng.
* [ ] WebSocket `/ws/car` kết nối được.
* [ ] Cảm biến siêu âm trả dữ liệu hợp lệ.
* [ ] Motor mặc định STOP.
* [ ] Chưa cấp nguồn motor nếu chưa kiểm tra xong cảm biến.
* [ ] ECHO 5V đã được hạ xuống 3.3V.
* [ ] Có thể gửi lệnh STOP khẩn cấp từ dashboard hoặc API.

---

## 19. Định hướng phát triển

Các hạng mục có thể mở rộng trong tương lai:

* Thêm cảm biến siêu âm phía trước.
* Bổ sung nút Emergency Stop trên dashboard.
* Thêm chế độ keyboard teleoperation.
* Hiển thị camera realtime trên frontend.
* Gửi detection result từ backend sang frontend.
* Lưu lịch sử telemetry.
* Tích hợp bản đồ di chuyển.
* Tối ưu AI pipeline chạy realtime.
* Thêm tracking ID cho người được phát hiện.
* Tách service AI thành worker riêng.
* Triển khai CI/CD cho backend và frontend.

---

## 20. Nguyên tắc thiết kế

Dự án tuân theo các nguyên tắc:

* Tách biệt rõ firmware, backend và frontend.
* Backend không xử lý trực tiếp logic phần cứng cấp thấp.
* Firmware chịu trách nhiệm đọc sensor và điều khiển motor.
* Backend chịu trách nhiệm điều phối, xử lý AI và ra quyết định.
* Frontend chỉ đóng vai trò dashboard điều khiển và giám sát.
* Media không lưu trực tiếp vào database.
* Mọi thao tác nguy hiểm với motor cần có cơ chế dừng an toàn.

---

## 21. Tác giả

Dự án được phát triển phục vụ mục tiêu nghiên cứu, học tập và triển khai hệ thống IoT Robot thông minh.

---

## 22. License

Dự án có thể sử dụng cho mục đích học tập, nghiên cứu và demo nội bộ.
Vui lòng bổ sung license cụ thể nếu triển khai thương mại hoặc công khai mã nguồn.
