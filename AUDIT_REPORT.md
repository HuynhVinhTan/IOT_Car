# SMART CAR RUNTIME FLOW AUDIT REPORT

**Date**: 2026-06-04  
**Status**: Backend imports PASS, Firmware build FAIL

---

## 1. WEBSOCKET CAMERA FLOW

### Endpoint

- **Publisher**: `POST /ws/cameras/{camera_id}/publish`
- **Location**: `app/api/routes/camera_ws.py:18`

### Data Format

- **ESP32-CAM sends**: Binary JPEG frames
- **Validation**: Checks for JPEG markers (`0xFF 0xD8` start, `0xFF 0xD9` end)
- **Max frame size**: Configurable via `CameraFrameHub.max_frame_bytes`

### Frame Processing Pipeline

```
ESP32-CAM → WebSocket binary → CameraFrameHub.handle_frame()
  ├─> Validation (JPEG markers, size limit)
  ├─> Rate limiting (max FPS check)
  ├─> Store in RAM: state.latest_frame_bytes
  ├─> Broadcast to viewers via WebSocket
  └─> NO Cloudinary upload
      NO Database save
      NO automatic AI analysis
```

### Latest Frame Storage

- **Location**: `CameraFrameHub.CameraStreamState.latest_frame_bytes` (RAM only)
- **Persistence**: None (volatile, lost on restart)
- **Access**: GET `/api/cameras/{camera_id}/latest-frame`

### AI Integration

- **Manual trigger**: POST `/api/cameras/{camera_id}/analyze-latest`
- **Process**: Reads latest frame from RAM → passes to `vision_pipeline_service`
- **NO automatic analysis** on frame arrival

### What's Missing

- ❌ No automatic Cloudinary upload for camera frames
- ❌ No database persistence for camera frames
- ❌ No automatic AI analysis
- ✅ Frame broadcast to viewers works
- ✅ Latest frame cached in RAM

---

## 2. CLOUDINARY UPLOAD FLOW

### Service

- **Class**: `MediaAssetService`
- **Location**: `app/services/media/media_asset_service.py`

### Current Usage

**ONLY** used for target face image uploads:

```python
# In FaceRegistryService.add_target_image()
asset = await self.media_service.upload_asset(
    file=file,
    folder=f"face_targets/{target_id}",
    purpose="face_target"
)
```

### Upload Targets

| Data Type          | Cloudinary? | DB Storage                    | Purpose                     |
| ------------------ | ----------- | ----------------------------- | --------------------------- |
| Camera frames      | ❌ NO       | ❌ NO                         | Real-time streaming only    |
| Target face images | ✅ YES      | ✅ YES (`media_assets` table) | Face recognition enrollment |
| Face snapshots     | ❌ NO       | ❌ NO                         | Not implemented             |
| AI results         | ❌ NO       | ❌ NO                         | Not implemented             |

### Database Records

When uploading to Cloudinary:

- Creates `MediaAsset` record with `secure_url`, `public_id`, `cloudinary_folder`
- Links via foreign key (e.g., `FaceTargetImage.media_asset_id`)

---

## 3. POST /api/faces/targets FLOW

### Endpoint

```
POST /api/faces/targets
Content-Type: multipart/form-data
Fields: display_name (required), notes (optional), image (optional)
```

### Request Flow

```
1. Receive multipart form data
2. Create FaceTarget record in DB
   └─> display_name, notes, status="ACTIVE"
3. IF image provided:
   a. Upload to Cloudinary
      └─> folder: face_targets/{target_id}
      └─> purpose: "face_target"
   b. Create FaceTargetImage record
      └─> links target_id to media_asset_id
   c. Generate embedding
      └─> FaceRecognitionService.enroll_target(image_bytes)
      └─> Uses InsightFace (REAL, not mock)
   d. Store embedding in FaceEmbedding table
      └─> provider="insightface"
      └─> dimension=512
      └─> embedding_json={"vector": [512 floats]}
   e. Rebuild recognition cache
      └─> FaceRecognitionService.build_cache()
4. Return FaceTargetSchema response
```

### AI Processing

- ✅ **REAL AI**: Uses InsightFace to generate embeddings
- ✅ **Reads from Cloudinary**: Image accessible via `secure_url`
- ✅ **Database persisted**: Embedding stored for future comparisons
- ✅ **Cache updated**: Recognition service cache rebuilt

### What Works

- ✅ Cloudinary upload functional
- ✅ Database persistence working
- ✅ AI embedding generation real (not mock)
- ✅ Target image accessible for future recognition

---

## 4. FIRMWARE PIN MAPPING AUDIT

### Current Mapping (pin_config.h)

```cpp
// Ultrasonic Sensors
RIGHT_ULTRASONIC_TRIG_PIN = 23   // Output OK
RIGHT_ULTRASONIC_ECHO_PIN = 35   // Input-only (OK)
LEFT_ULTRASONIC_TRIG_PIN = 22    // Output OK
LEFT_ULTRASONIC_ECHO_PIN = 34    // Input-only (OK)

// L298N Motor Driver
LEFT_MOTOR_ENA_PIN = 18          // PWM OK
LEFT_MOTOR_IN1_PIN = 32          // Output OK
LEFT_MOTOR_IN2_PIN = 33          // Output OK
RIGHT_MOTOR_ENB_PIN = 19         // PWM OK
RIGHT_MOTOR_IN3_PIN = 25         // Output OK
RIGHT_MOTOR_IN4_PIN = 26         // Output OK

// Speed Sensors
SPEED_SENSOR_RIGHT_PIN = 13      // Input OK
SPEED_SENSOR_LEFT_PIN = 27       // Input OK
```

### User Requested Mapping

```
Ultrasonic right: TRIG=23, ECHO=35 ✅ MATCHES
Ultrasonic left: TRIG=22, ECHO=34 ✅ MATCHES
L298N: ENA=2, ENB=19, IN1=32, IN2=33, IN3=25, IN4=26
       ❌ ENA MISMATCH (firmware=18, user=2)
Speed right: GPIO13 ✅ MATCHES
Speed left: GPIO27 ✅ MATCHES
```

### Hardware Constraints & Risks

#### ✅ CORRECT (Input-Only GPIOs)

- GPIO34, GPIO35 used for ECHO (input-only pins)
- Cannot be outputs, perfect for reading ultrasonic ECHO

#### ⚠️ VOLTAGE DIVIDER REQUIRED

- **HC-SR04 ECHO outputs 5V**
- **ESP32 GPIO max input = 3.3V**
- **MUST use voltage divider**: 5V → 3.3V
- Recommended: R1=1kΩ, R2=2kΩ (2:1 divider)

#### ✅ BOOT STRAP PIN AVOIDED

- User requested GPIO2 for ENA
- Firmware uses GPIO18 instead
- **GOOD DECISION**: GPIO2 is boot strap pin
  - HIGH at boot = normal boot
  - LOW at boot = download mode
  - Using for PWM could cause boot issues

#### 🔍 DISCREPANCY

- **User spec**: ENA=GPIO2
- **Firmware**: ENA=GPIO18
- **Reason**: Likely to avoid GPIO2 boot issues
- **Action**: Verify with user if GPIO18 is acceptable

### Pin Capabilities Check

| Pin    | Type       | Usage   | PWM? | Notes                     |
| ------ | ---------- | ------- | ---- | ------------------------- |
| GPIO23 | Output     | TRIG    | No   | OK                        |
| GPIO35 | Input-only | ECHO    | No   | OK, needs voltage divider |
| GPIO22 | Output     | TRIG    | No   | OK                        |
| GPIO34 | Input-only | ECHO    | No   | OK, needs voltage divider |
| GPIO18 | Output     | ENA PWM | Yes  | OK                        |
| GPIO19 | Output     | ENB PWM | Yes  | OK                        |
| GPIO32 | Output     | IN1     | No   | OK                        |
| GPIO33 | Output     | IN2     | No   | OK                        |
| GPIO25 | Output     | IN3     | Yes  | OK                        |
| GPIO26 | Output     | IN4     | Yes  | OK                        |
| GPIO13 | Input      | Speed   | No   | OK                        |
| GPIO27 | Input      | Speed   | No   | OK                        |

---

## 5. FIRMWARE BUILD STATUS

### ❌ BUILD FAILS

```
Error: 'Engine', 'DistanceSensorArray', 'CliffSensorArray', etc. not declared
File: src/car_controller.cpp
```

### Root Cause

- `car_controller.cpp` uses classes without including headers
- `car_controller.h` declares member variables but doesn't include type definitions

### Missing Includes (car_controller.h needs)

```cpp
#include "car_types.h"
#include "engine.h"
#include "distance_sensor_array.h"
#include "cliff_sensor_array.h"
#include "speed_sensor.h"
#include "camera.h"
#include "local_status_button.h"
#include "battery_monitor.h"
#include "lcd_display.h"
#include "command_parser.h"
#include "telemetry.h"
#include "safety_guard.h"
```

### Build Command

```bash
Set-Location -Path "D:\AA\IOT\project\smart_car\firmware\car_controller_esp32"
C:\Users\ASUS-PRO\.platformio\penv\Scripts\platformio.exe run
```

---

## SUMMARY

### ✅ Working

1. Backend imports clean (no circular dependencies)
2. WebSocket camera frame reception (binary JPEG)
3. Latest frame caching in RAM
4. Frame broadcast to viewers
5. POST /api/faces/targets endpoint functional
6. Cloudinary upload for target images
7. Real AI embedding generation (InsightFace)
8. Database persistence for targets and embeddings

### ❌ Not Implemented / Issues

1. Camera frames NOT uploaded to Cloudinary automatically
2. Camera frames NOT saved to database
3. No automatic AI analysis on frame arrival
4. Firmware build fails (missing includes)
5. Pin mapping discrepancy (ENA: GPIO2 vs GPIO18)
6. No voltage divider reminder in firmware comments

### ⚠️ Hardware Warnings

1. **CRITICAL**: ECHO pins (34, 35) need 5V→3.3V voltage dividers
2. GPIO2 bootstrap pin avoided in firmware (good)
3. Confirm GPIO18 acceptable for ENA instead of GPIO2

### 📋 Next Steps (If Requested)

1. Fix firmware includes to enable build
2. Add voltage divider circuit diagram
3. Implement camera frame persistence (Cloudinary + DB)
4. Add automatic AI analysis trigger
5. Confirm pin mapping with user
