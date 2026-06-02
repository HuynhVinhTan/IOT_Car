#pragma once

#include "esp_camera.h"
#include <cstddef>

constexpr bool ENABLE_LOCAL_HTTP_DEBUG = false;
constexpr bool ENABLE_WS_CAMERA_PUBLISHER = true;

constexpr unsigned long FRAME_INTERVAL_MS = 64;

constexpr unsigned long HEARTBEAT_INTERVAL_MS = 5000;
constexpr unsigned long WIFI_CONNECT_TIMEOUT_MS = 30000;
constexpr unsigned long WIFI_RETRY_DELAY_MS = 500;

constexpr framesize_t CAMERA_FRAME_SIZE = FRAMESIZE_QVGA;

constexpr int CAMERA_JPEG_QUALITY = 8;

constexpr std::size_t MAX_LOCAL_FRAME_BYTES = 200000;

constexpr bool ENABLE_WIFI_SCAN_LOG = true;

constexpr bool ENABLE_FRAME_LOG = true;
constexpr unsigned long FRAME_LOG_EVERY = 30;