#include "joystick_client.h"
#include "alert_output.h"
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

namespace JoystickClient {

  static AppConfig appConfig;
  static WebSocketsClient webSocket;
  static unsigned long lastWsConnect = 0;

  static void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
      case WStype_DISCONNECTED:
        Serial.println("[WS] Disconnected!");
        break;
      case WStype_CONNECTED:
        Serial.printf("[WS] Connected to url: %s\n", payload);
        break;
      case WStype_TEXT:
        {
          // Serial.printf("[WS] Message: %s\n", payload);
          JsonDocument doc;
          DeserializationError err = deserializeJson(doc, payload);
          if (!err) {
            String msgType = doc["type"] | "";
            if (msgType == "detection_event") {
              String event = doc["event"] | "";
              if (event == "person_detected") {
                AlertOutput::triggerAlert();
              }
            }
          }
        }
        break;
      case WStype_BIN:
      case WStype_PING:
      case WStype_PONG:
      case WStype_ERROR:
      case WStype_FRAGMENT_TEXT_START:
      case WStype_FRAGMENT_BIN_START:
      case WStype_FRAGMENT:
      case WStype_FRAGMENT_FIN:
        break;
    }
  }

  void init(const AppConfig& config) {
    appConfig = config;

    Serial.printf("[Client] Connecting to WiFi %s\n", config.wifiSsid.c_str());
    WiFi.begin(config.wifiSsid.c_str(), config.wifiPassword.c_str());

    int retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 20) {
      delay(500);
      Serial.print(".");
      retries++;
    }
    Serial.println();
    
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("[Client] WiFi connected. IP: " + WiFi.localIP().toString());
    } else {
      Serial.println("[Client] WiFi connection failed.");
      return;
    }

    // Initialize WebSocket for telemetry
    String wsUrl = "/ws/telemetry";
    
    // Add token query if needed
    if (appConfig.joystickToken.length() > 0) {
        wsUrl += "?token=" + appConfig.joystickToken;
    }

    if (appConfig.backendTls) {
      webSocket.beginSSL(appConfig.backendHost.c_str(), appConfig.backendPort, wsUrl.c_str());
    } else {
      webSocket.begin(appConfig.backendHost.c_str(), appConfig.backendPort, wsUrl.c_str());
    }
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(3000);
  }

  void sendCommand(ButtonInput::CommandState cmd) {
    if (WiFi.status() != WL_CONNECTED) return;

    WiFiClient client;
    WiFiClientSecure clientSecure;
    HTTPClient http;
    
    String url = (appConfig.backendTls ? "https://" : "http://") + 
                 appConfig.backendHost + ":" + String(appConfig.backendPort) + 
                 "/api/car/command";

    if (appConfig.backendTls) {
      clientSecure.setInsecure(); // Skip certificate validation for simplicity/compatibility
      http.begin(clientSecure, url);
    } else {
      http.begin(client, url);
    }

    http.addHeader("Content-Type", "application/json");
    if (appConfig.joystickToken.length() > 0) {
      http.addHeader("Authorization", "Bearer " + appConfig.joystickToken);
    }

    JsonDocument doc;
    if (cmd == ButtonInput::CMD_STOP) {
      doc["command"] = "REMOTE_STOP";
    } else {
      doc["command"] = "REMOTE_DRIVE";
      doc["source"] = appConfig.joystickId.length() > 0 ? appConfig.joystickId : "joystick_bridge_esp8266";
      
      int left = 0, right = 0;
      switch (cmd) {
        case ButtonInput::CMD_FORWARD:  left = 100; right = 100; break;
        case ButtonInput::CMD_BACKWARD: left = -100; right = -100; break;
        case ButtonInput::CMD_LEFT:     left = -80; right = 80; break;
        case ButtonInput::CMD_RIGHT:    left = 80; right = -80; break;
        default: break;
      }
      doc["left_motor_speed"] = left;
      doc["right_motor_speed"] = right;
    }

    String payload;
    serializeJson(doc, payload);

    int httpResponseCode = http.POST(payload);
    
    if (httpResponseCode > 0) {
      // Serial.printf("[HTTP] POST %d\n", httpResponseCode);
    } else {
      Serial.printf("[HTTP] Error: %s\n", http.errorToString(httpResponseCode).c_str());
    }
    
    http.end();
  }

  void loop() {
    if (WiFi.status() == WL_CONNECTED) {
      webSocket.loop();
    }
  }

}