# Runtime Flow & Hardware Mapping Audit

Dưới đây là báo cáo audit dựa trên source code hiện tại:

## 1. WebSocket Camera Flow

- **Endpoint nhận frame:** `/ws/cameras/{camera_id}/publish` (hàm `publish_camera_frames`).
- **Data format ESP32-CAM gửi:** Gửi **binary JPEG** (`message.get("bytes")`). Ngoài ra có thể gửi text/JSON cho heartbeat. Frame được validate bằng header/footer chuẩn của JPEG (`\xff\xd8` và `\xff\xd9`).
- **Lưu vào Cloudinary?** **Không**. Frame stream thời gian thực không được upload lên Cloudinary.
- **Lưu trong RAM?** **Có**. `CameraFrameHub` giữ frame mới nhất của mỗi camera trong biến `state.latest_frame_bytes` trên RAM.
- **Gửi sang Frontend?** **Có**. Frontend (viewer) kết nối qua `/ws/cameras/{camera_id}/view` và backend sẽ broadcast binary frame (`viewer.send_bytes()`) tới các kết nối này.
- **Gửi sang AI?** Khung hình được lưu trong RAM, AI có thể đọc khung hình này (ví dụ qua API `/api/cameras/{camera_id}/analyze-latest` hoặc endpoint `/api/faces/verify`). Hiện tại AI xử lý khi có request gọi tới các endpoint phân tích chứ không chạy ngầm liên tục đè lên stream (trừ khi có worker riêng gọi liên tục).
- **Lưu DB?** **Không**. Frame stream không được lưu vào Database.

## 2. Cloudinary Media Asset

- **Service xử lý:** `CloudinaryMediaService` và `MediaAssetService`.
- **Đang upload loại dữ liệu nào?** Hiện tại chủ yếu upload **Face target image** (ảnh dùng để nhận diện khuôn mặt).
- **Mục đích (Purpose):** Khi đăng ký target, ảnh được upload lên với thư mục `face_targets/{target_id}`. Các media asset khác có thể dùng service này nhưng code hiện tại sử dụng nó chủ yếu cho việc lưu ảnh mục tiêu. Ảnh stream từ camera và snapshot realtime không tự động upload.
- **Lưu DB?** **Có**. Sau khi upload, URL (`secure_url`) và `public_id` được lưu vào bảng `MediaAsset` thông qua repository.

## 3. POST Upload Target Image

- **Endpoint:** `/api/faces/targets` (method POST).
- **Request format:** `multipart/form-data` chứa `display_name`, `notes` và file `image`.
- **Upload Cloudinary?** **Có**. Gọi `FaceRegistryService.add_target_image` -> `MediaAssetService.upload_asset` -> Cloudinary.
- **Lưu DB?** **Có**. Tạo `FaceTarget`, lưu thông tin asset vào `FaceTargetImage` (kèm `media_asset_id`), và lưu embedding vector vào `FaceEmbedding`.
- **AI có đọc được ảnh không?** **Có**. Ngay trong luồng upload, `file_content` được đọc trong RAM và đưa trực tiếp vào `recognition_service.enroll_target()` để sinh embedding vector.
- **AI thật hay mock?** **Thật**. Sử dụng model của InsightFace (đã được nạp ở `FaceRecognitionService`) để nhận diện và sinh vector 512 chiều.

## 4. Firmware & Hardware Mapping

- **Firmware path:** `smart_car/firmware/car_controller_esp32/`
- **Pin Mapping Audit:**
  - **Ultrasonic Right:** TRIG 23, ECHO 35 (Khớp).
  - **Ultrasonic Left:** TRIG 22, ECHO 34 (Khớp).
  - **Motor L298N Left:** IN1 32, IN2 33 (Khớp). Tuy nhiên **ENA đang cấu hình là GPIO18** (chứ không phải GPIO2 như yêu cầu).
  - **Motor L298N Right:** ENB 19, IN3 25, IN4 26 (Khớp).
  - **Speed Sensors:** Right 13, Left 27 (Khớp).

- **Phân tích rủi ro & Cảnh báo:**
  1. **GPIO2 Bootstrap (Nếu đổi ENA thành GPIO2):** GPIO2 là một strapping pin quan trọng của ESP32. Trạng thái của chân này lúc khởi động (boot) quyết định chế độ boot của chip. Nếu L298N ENA kéo GPIO2 lên cao (pull-up) hoặc gây nhiễu trong quá trình cấp nguồn, ESP32 sẽ **không thể boot** hoặc bị kẹt ở chế độ Download Mode. Khuyến cáo: Giữ ENA ở GPIO18 như code hiện tại hoặc chuyển sang các chân an toàn khác (ví dụ GPIO12, 14 nếu không dùng).
  2. **GPIO34/35 Input-only:** Đúng, 2 chân này không có điện trở pull-up/pull-down nội và chỉ nhận tín hiệu input, rất phù hợp cho chân ECHO.
  3. **ECHO 5V chia áp:** Trong `pin_config.h` có comment rõ: `"HC-SR04 ECHO 5V must be divided to 3.3V before entering GPIO34/35"`. ESP32 chạy mức logic 3.3V, nếu cắm thẳng 5V từ HC-SR04 vào ECHO sẽ gây cháy hoặc hỏng chân GPIO theo thời gian. Bắt buộc phải dùng mạch chia áp (voltage divider, ví dụ dùng điện trở 1k và 2k) để hạ xuống ~3.3V.
  4. **Duplicate Defines:** Trong `pin_config.h` có định nghĩa lại các thông số PWM (`MOTOR_PWM_FREQUENCY_HZ`, `MAX_MOTOR_SPEED`,...) vốn đã có ở `car_types.h`. Điều này có thể gây lỗi compile (multiple definition/redefinition), cần dọn dẹp lại.
