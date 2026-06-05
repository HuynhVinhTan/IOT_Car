#include <Arduino.h>
#include <WiFi.h>
#include <WebSocketsClient.h>
#include "esp_camera.h"
#include "esp_wifi.h"

#include "camera_pins.h"
#include "camera_runtime_config.h"

#include "app_config.h"
#include "config_portal.h"
#include "serial_cli.h"

WebSocketsClient backendWebSocket;
AppConfig appConfig;

bool wsConnected = false;

String buildCameraWsPath() {
  return String("/ws/cameras/") + appConfig.cameraId + "/publish?token=" + appConfig.cameraToken;
}

framesize_t parseFrameSize(const String& value) {
  if (value == "QQVGA") return FRAMESIZE_QQVGA;
  if (value == "QVGA") return FRAMESIZE_QVGA;
  if (value == "VGA") return FRAMESIZE_VGA;
  return FRAMESIZE_QVGA;
}

camera_grab_mode_t parseGrabMode(const String& value) {
  if (value == "LATEST") return CAMERA_GRAB_LATEST;
  return CAMERA_GRAB_WHEN_EMPTY;
}

void setupWiFi() {
  Serial.println("[BOOT] Step 1 WiFi");
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  esp_wifi_set_ps(WIFI_PS_NONE);
  WiFi.disconnect(true);
  delay(1000);

  WiFi.begin(appConfig.wifiSsid.c_str(), appConfig.wifiPassword.c_str());
  unsigned long startAt = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    if (millis() - startAt > 30000) ESP.restart();
  }
  Serial.println("[WiFi] Connected");
}

bool setupCamera() {
  Serial.println("[BOOT] Step 2 Camera");
  camera_config_t config = {};
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM; config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM; config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM; config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM; config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM; config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM; config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM; config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM; config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = appConfig.xclkFreqHz;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = parseFrameSize(appConfig.frameSize);
  config.jpeg_quality = appConfig.jpegQuality;
  config.fb_count = appConfig.fbCount;
  config.grab_mode = parseGrabMode(appConfig.grabMode);

  if (psramFound()) {
    config.fb_location = CAMERA_FB_IN_PSRAM;
  } else {
    config.fb_count = 1;
    config.fb_location = CAMERA_FB_IN_DRAM;
  }

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("[CAM] Init FAILED");
    return false;
  }

  if (appConfig.cameraDiagEnabled) {
    bool success = false;
    for (int i = 1; i <= 5; i++) {
      Serial.printf("[CAM-DIAG] Capture attempt %d/5\n", i);
      camera_fb_t *fb = esp_camera_fb_get();
      if (fb) {
        Serial.printf("[CAM-DIAG] Success attempt %d, size=%u\n", i, fb->len);
        esp_camera_fb_return(fb);
        success = true;
        break;
      }
      delay(300);
    }
    if (!success) Serial.println("[CAM-DIAG] FAILED after 5 attempts");
  }
  return true;
}

void setupBackendWebSocket() {
  Serial.println("[BOOT] Step 3 WebSocket");
  
  // Debug info
  Serial.printf("[WS] Host: %s, Port: %u, TLS: %s\n", appConfig.backendHost.c_str(), appConfig.backendPort, appConfig.backendTls ? "true" : "false");
  
  if (appConfig.backendTls) {
    backendWebSocket.beginSSL(appConfig.backendHost.c_str(), appConfig.backendPort, buildCameraWsPath().c_str());
  } else {
    backendWebSocket.begin(appConfig.backendHost.c_str(), appConfig.backendPort, buildCameraWsPath().c_str());
  }
  backendWebSocket.setReconnectInterval(5000);
}

void setup() {
  Serial.begin(115200);
  Serial.println("[BUILD] CAMERA_CONFIG_PORTAL_RUNTIME_V1");
  
  loadAppConfig(appConfig);
  if (!appConfig.valid) startConfigPortal("SmartCar-Setup");

  setupWiFi();
  if (!setupCamera()) {
    Serial.println("[CAM] Hardware init failed. Check ribbon/power.");
  }
  setupBackendWebSocket();
}

void loop() {
  backendWebSocket.loop();
}