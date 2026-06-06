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

  // DNS fallback
  WiFi.config(INADDR_NONE, INADDR_NONE, INADDR_NONE, IPAddress(8,8,8,8), IPAddress(1,1,1,1));

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

  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  Serial.println("[NTP] Syncing time...");
  unsigned long ntpStart = millis();
  while (time(nullptr) < 100000) {
    if (millis() - ntpStart > 10000) {
      Serial.println("[NTP] Sync timeout");
      break;
    }
    delay(500);
  }
  if (time(nullptr) > 100000) {
    Serial.println("[TLS] NTP synced");
  }

  String wsPath = buildCameraWsPath();
  
  Serial.printf("[WS] path: %s\n", wsPath.c_str());
  Serial.printf("[WS] free heap: %u\n", ESP.getFreeHeap());
  Serial.printf("[WS] free psram: %u\n", ESP.getFreePsram());
  Serial.printf("[WS] WiFi RSSI: %d\n", WiFi.RSSI());
  
  IPAddress dnsResult;
  WiFi.hostByName(appConfig.backendHost.c_str(), dnsResult);
  Serial.printf("[WS] DNS result for %s: %s\n", appConfig.backendHost.c_str(), dnsResult.toString().c_str());

  Serial.printf("[WS] Host: %s, Port: %u, TLS: %s\n", appConfig.backendHost.c_str(), appConfig.backendPort, appConfig.backendTls ? "true" : "false");
  
  if (appConfig.backendTls) {
    Serial.println("[TLS] mode=standard (CA cert required if not trusted)");
    backendWebSocket.beginSSL(appConfig.backendHost.c_str(), appConfig.backendPort, wsPath.c_str(), "");
  } else {
    backendWebSocket.begin(appConfig.backendHost.c_str(), appConfig.backendPort, wsPath.c_str());
  }

  backendWebSocket.onEvent([](WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
      case WStype_DISCONNECTED:
        Serial.println("[WS] WStype_DISCONNECTED");
        wsConnected = false;
        break;
      case WStype_CONNECTED:
        Serial.printf("[WS] WStype_CONNECTED to url: %s\n", payload);
        wsConnected = true;
        break;
      case WStype_TEXT:
        Serial.printf("[WS] WStype_TEXT: %s\n", payload);
        break;
      case WStype_ERROR:
        Serial.printf("[WS] WStype_ERROR: %s (Heap: %u, PSRAM: %u)\n", payload ? (const char*)payload : "null", ESP.getFreeHeap(), ESP.getFreePsram());
        break;
      default:
        break;
    }
  });

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

unsigned long lastFrameSent = 0;
int frameCounter = 0;

void captureAndSendFrameIfDue() {
  if (!wsConnected) return;
  if (millis() - lastFrameSent < 100) return; // 10 FPS limit

  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) return;

  if (backendWebSocket.sendBIN(fb->buf, fb->len)) {
    frameCounter++;
    Serial.printf("[CAM] Frame sent #%d, size=%u\n", frameCounter, fb->len);
    lastFrameSent = millis();
  }
  
  esp_camera_fb_return(fb);
}

void loop() {
  backendWebSocket.loop();
  captureAndSendFrameIfDue();
}
