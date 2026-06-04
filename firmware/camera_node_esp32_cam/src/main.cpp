#include <Arduino.h>
#include <WiFi.h>
#include <WebSocketsClient.h>
#include "esp_camera.h"

#include "camera_pins.h"
#include "camera_runtime_config.h"

#include "app_config.h"
#include "config_portal.h"
#include "serial_cli.h"

WebSocketsClient backendWebSocket;
AppConfig appConfig;

bool wsConnected = false;
unsigned long lastFrameAt = 0;
unsigned long lastHeartbeatAt = 0;
unsigned long frameSentCount = 0;

String buildCameraWsPath() {
  return String("/ws/cameras/") + appConfig.cameraId + "/publish?token=" + appConfig.cameraToken;
}

void logWifiNetworks() {
#if ENABLE_WIFI_SCAN_LOG == 1
  Serial.println("[WiFi] Scanning...");
  int count = WiFi.scanNetworks();

  Serial.printf("[WiFi] Found %d networks\n", count);

  for (int i = 0; i < count; i++) {
    Serial.printf(
      "[WiFi] %d: SSID='%s', RSSI=%d, CH=%d, ENC=%d\n",
      i + 1,
      WiFi.SSID(i).c_str(),
      WiFi.RSSI(i),
      WiFi.channel(i),
      WiFi.encryptionType(i)
    );
  }
#endif
}

void setupWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.disconnect(true);
  delay(1000);

  logWifiNetworks();

  Serial.print("[WiFi] Connecting to ");
  Serial.println(appConfig.wifiSsid);

  WiFi.begin(appConfig.wifiSsid.c_str(), appConfig.wifiPassword.c_str());

  unsigned long startAt = millis();

  while (WiFi.status() != WL_CONNECTED) {
    delay(WIFI_RETRY_DELAY_MS);
    Serial.print(".");

    if (millis() - startAt > WIFI_CONNECT_TIMEOUT_MS) {
      Serial.println();
      Serial.print("[WiFi] Connect timeout. status=");
      Serial.println(WiFi.status());
      Serial.println("[WiFi] Restarting...");
      ESP.restart();
    }
  }

  Serial.println();
  Serial.println("[WiFi] Connected");
  Serial.print("[WiFi] IP: ");
  Serial.println(WiFi.localIP());
  Serial.print("[WiFi] RSSI: ");
  Serial.println(WiFi.RSSI());
}

bool setupCamera() {
  camera_config_t config = {};

  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;

  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;

  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = CAMERA_FRAME_SIZE;
  config.jpeg_quality = appConfig.jpegQuality;

  if (psramFound()) {
    Serial.println("[CAM] PSRAM found");
    config.fb_count = 2;
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.grab_mode = CAMERA_GRAB_LATEST;
  } else {
    Serial.println("[CAM] PSRAM not found");
    config.fb_count = 1;
    config.fb_location = CAMERA_FB_IN_DRAM;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  }

  esp_err_t error = esp_camera_init(&config);

  if (error != ESP_OK) {
    Serial.printf("[CAM] Init failed: 0x%x\n", error);
    return false;
  }

  sensor_t *sensor = esp_camera_sensor_get();

  if (sensor) {
    sensor->set_framesize(sensor, CAMERA_FRAME_SIZE);
    sensor->set_quality(sensor, appConfig.jpegQuality);

    sensor->set_brightness(sensor, 0);
    sensor->set_contrast(sensor, 0);
    sensor->set_saturation(sensor, 0);

    sensor->set_whitebal(sensor, 1);
    sensor->set_awb_gain(sensor, 1);
    sensor->set_exposure_ctrl(sensor, 1);
    sensor->set_gain_ctrl(sensor, 1);

    sensor->set_lenc(sensor, 1);
    sensor->set_bpc(sensor, 1);
    sensor->set_wpc(sensor, 1);

    sensor->set_vflip(sensor, 0);
    sensor->set_hmirror(sensor, 0);
  }

  Serial.println("[CAM] Init OK");
  return true;
}

void sendHeartbeat() {
  if (!wsConnected) {
    return;
  }

  String message = String("{") +
                   "\"type\":\"camera_heartbeat\"," +
                   "\"camera_id\":\"" + appConfig.cameraId + "\"," +
                   "\"frame_sent_count\":" + String(frameSentCount) + "," +
                   "\"free_heap\":" + String(ESP.getFreeHeap()) + "," +
                   "\"rssi\":" + String(WiFi.RSSI()) +
                   "}";

  backendWebSocket.sendTXT(message);
}

void publishFrame() {
  if (!wsConnected) {
    return;
  }

  camera_fb_t *frameBuffer = esp_camera_fb_get();

  if (!frameBuffer) {
    Serial.println("[CAM] Capture failed");
    return;
  }

  if (frameBuffer->format != PIXFORMAT_JPEG || frameBuffer->len == 0) {
    Serial.println("[CAM] Invalid frame");
    esp_camera_fb_return(frameBuffer);
    return;
  }

  if (frameBuffer->len > MAX_LOCAL_FRAME_BYTES) {
    Serial.printf("[CAM] Frame too large: %u bytes\n", frameBuffer->len);
    esp_camera_fb_return(frameBuffer);
    return;
  }

  bool sent = backendWebSocket.sendBIN(frameBuffer->buf, frameBuffer->len);

  if (sent) {
    frameSentCount++;

#if ENABLE_FRAME_LOG == 1
    if (frameSentCount % FRAME_LOG_EVERY == 0) {
      Serial.printf("[CAM] Frame sent #%lu, size=%u bytes\n", frameSentCount, frameBuffer->len);
    }
#endif
  } else {
    Serial.printf("[CAM] Send failed, size=%u bytes\n", frameBuffer->len);
  }

  esp_camera_fb_return(frameBuffer);
}

void onBackendWebSocketEvent(WStype_t type, uint8_t *payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      wsConnected = false;
      Serial.println("[WS] Disconnected");
      break;

    case WStype_CONNECTED:
      wsConnected = true;
      Serial.println("[WS] Connected");

      backendWebSocket.sendTXT(
        String("{") +
        "\"type\":\"camera_hello\"," +
        "\"camera_id\":\"" + appConfig.cameraId + "\"," +
        "\"mode\":\"WS_PUBLISHER_ONLY\"," +
        "\"frame_size\":\"QVGA\"," +
        "\"jpeg_quality\":" + String(appConfig.jpegQuality) + "," +
        "\"frame_interval_ms\":" + String(appConfig.frameIntervalMs) +
        "}"
      );
      break;

    case WStype_TEXT:
      Serial.print("[WS] Text: ");
      Serial.write(payload, length);
      Serial.println();
      break;

    case WStype_ERROR:
      Serial.println("[WS] Error");
      break;

    default:
      break;
  }
}

void setupBackendWebSocket() {
  String path = buildCameraWsPath();

  Serial.println("[WS] Setup");
  Serial.print("[WS] Host: ");
  Serial.println(appConfig.backendHost);
  Serial.print("[WS] Port: ");
  Serial.println(appConfig.backendPort);
  Serial.print("[WS] TLS: ");
  Serial.println(appConfig.backendTls ? "true" : "false");
  Serial.print("[WS] Path: ");
  Serial.println(path); // Token is printed here? Wait! 
  // Let's replace the token in the log to be safe:
  String safePath = path;
  int tokenIdx = safePath.indexOf("token=");
  if (tokenIdx > 0) safePath = safePath.substring(0, tokenIdx + 6) + "******";
  Serial.println(safePath);

  if (appConfig.backendTls) {
    backendWebSocket.beginSSL(appConfig.backendHost.c_str(), appConfig.backendPort, path.c_str());
  } else {
    backendWebSocket.begin(appConfig.backendHost.c_str(), appConfig.backendPort, path.c_str());
  }

  backendWebSocket.onEvent(onBackendWebSocketEvent);
  backendWebSocket.setReconnectInterval(5000);
  backendWebSocket.enableHeartbeat(15000, 3000, 2);
}

bool isSetupButtonPressed() {
  pinMode(SETUP_BUTTON_PIN, INPUT_PULLUP);
  delay(10);
  bool pressed = (digitalRead(SETUP_BUTTON_PIN) == LOW);
  return pressed;
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\nSmart Car AI - ESP32-CAM WS Publisher");
  
  bool setupPressed = isSetupButtonPressed();
  
  loadAppConfig(appConfig);
  printSafeAppConfig(appConfig);

  // If button is held during boot or config is invalid, launch portal
  if (setupPressed || !appConfig.valid) {
    if (setupPressed) Serial.println("Setup button pressed!");
    else Serial.println("Config is missing/invalid.");
    
#if defined(ENABLE_CONFIG_PORTAL) && ENABLE_CONFIG_PORTAL == 1
    startConfigPortal("SmartCar-Setup");
#else
    Serial.println("Config portal disabled in build! Halting.");
    while (true) { delay(1000); }
#endif
  }

  serialCliBegin(appConfig);

  setupWiFi();

  if (!setupCamera()) {
    delay(5000);
    ESP.restart();
  }

  if (ENABLE_WS_CAMERA_PUBLISHER) {
    setupBackendWebSocket();
  }
}

void loop() {
  serialCliTick(appConfig);

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WiFi] Lost connection. Restarting...");
    delay(1000);
    ESP.restart();
  }

  if (ENABLE_WS_CAMERA_PUBLISHER) {
    backendWebSocket.loop();
  }

  unsigned long now = millis();

  if (ENABLE_WS_CAMERA_PUBLISHER && wsConnected && now - lastHeartbeatAt >= HEARTBEAT_INTERVAL_MS) {
    lastHeartbeatAt = now;
    sendHeartbeat();
  }

  if (ENABLE_WS_CAMERA_PUBLISHER && wsConnected && now - lastFrameAt >= appConfig.frameIntervalMs) {
    lastFrameAt = now;
    publishFrame();
  }
}