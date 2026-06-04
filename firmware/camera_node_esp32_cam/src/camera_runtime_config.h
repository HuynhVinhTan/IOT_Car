#pragma once

#include "esp_camera.h"
#include <cstddef>

constexpr bool ENABLE_LOCAL_HTTP_DEBUG = false;
constexpr bool ENABLE_WS_CAMERA_PUBLISHER = true;

constexpr unsigned long HEARTBEAT_INTERVAL_MS = 5000;
constexpr unsigned long WIFI_CONNECT_TIMEOUT_MS = 30000;
constexpr unsigned long WIFI_RETRY_DELAY_MS = 500;

constexpr framesize_t CAMERA_FRAME_SIZE = FRAMESIZE_QVGA;

constexpr std::size_t MAX_LOCAL_FRAME_BYTES = 200000;

#ifndef ENABLE_WIFI_SCAN_LOG
#define ENABLE_WIFI_SCAN_LOG 1
#endif

#ifndef ENABLE_FRAME_LOG
#define ENABLE_FRAME_LOG 1
#endif
constexpr unsigned long FRAME_LOG_EVERY = 30;

// Setup button GPIO. For ESP32-CAM, GPIO0 is used for BOOT button,
// but it's also XCLK. So we only read it at very early boot.
#ifndef SETUP_BUTTON_PIN
#define SETUP_BUTTON_PIN 0
#endif