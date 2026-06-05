#include "app_config.h"
#include <LittleFS.h>
#include <ArduinoJson.h>

static const char* CONFIG_FILE = "/config.json";

static bool fsReady = false;

static void ensureFS() {
  if (!fsReady) {
    fsReady = LittleFS.begin();
    if (!fsReady) {
      Serial.println("[Config] LittleFS mount failed, formatting...");
      LittleFS.format();
      fsReady = LittleFS.begin();
    }
  }
}

void loadConfig(AppConfig &config) {
  ensureFS();

  // Set safe defaults
  config.wifiSsid      = "";
  config.wifiPassword  = "";
  config.backendHost   = "";
  config.backendPort   = 443;
  config.backendTls    = true;
  config.joystickId    = "";
  config.joystickToken = "";
  config.valid         = false;

  if (!LittleFS.exists(CONFIG_FILE)) {
    Serial.println("[Config] No config file found.");
    return;
  }

  File f = LittleFS.open(CONFIG_FILE, "r");
  if (!f) {
    Serial.println("[Config] Failed to open config file.");
    return;
  }

  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, f);
  f.close();

  if (err) {
    Serial.printf("[Config] JSON parse error: %s\n", err.c_str());
    return;
  }

  config.wifiSsid      = doc["wifi_ssid"]   | "";
  config.wifiPassword  = doc["wifi_pass"]   | "";
  config.backendHost   = doc["be_host"]     | "";
  config.backendPort   = doc["be_port"]     | 443;
  config.backendTls    = doc["be_tls"]      | true;
  config.joystickId    = doc["joy_id"]      | "";
  config.joystickToken = doc["joy_token"]   | "";

  config.valid = isAppConfigValid(config);
  Serial.println("[Config] Config loaded.");
}

void saveConfig(const AppConfig &config) {
  ensureFS();

  JsonDocument doc;
  doc["wifi_ssid"]  = config.wifiSsid;
  doc["wifi_pass"]  = config.wifiPassword;
  doc["be_host"]    = config.backendHost;
  doc["be_port"]    = config.backendPort;
  doc["be_tls"]     = config.backendTls;
  doc["joy_id"]     = config.joystickId;
  doc["joy_token"]  = config.joystickToken;

  File f = LittleFS.open(CONFIG_FILE, "w");
  if (!f) {
    Serial.println("[Config] Failed to open config file for write.");
    return;
  }
  serializeJson(doc, f);
  f.close();
  Serial.println("[Config] Config saved.");
}

bool isAppConfigValid(const AppConfig &config) {
  return config.wifiSsid.length() > 0 &&
         config.backendHost.length() > 0 &&
         config.backendPort > 0;
}

void printConfig(const AppConfig &config) {
  Serial.println("--- Joystick Bridge Config ---");
  Serial.printf("  WiFi SSID    : %s\n", config.wifiSsid.c_str());
  Serial.printf("  WiFi Pass    : %s\n", config.wifiPassword.length() > 0 ? "******" : "(empty)");
  Serial.printf("  Backend Host : %s\n", config.backendHost.c_str());
  Serial.printf("  Backend Port : %d\n", config.backendPort);
  Serial.printf("  Backend TLS  : %s\n", config.backendTls ? "true" : "false");
  Serial.printf("  Joystick ID  : %s\n", config.joystickId.length() > 0 ? config.joystickId.c_str() : "(empty)");
  Serial.printf("  Token        : %s\n", config.joystickToken.length() > 0 ? "******" : "(empty)");
  Serial.printf("  Valid        : %s\n", config.valid ? "true" : "false");
  Serial.println("------------------------------");
}

void clearConfig() {
  ensureFS();
  LittleFS.remove(CONFIG_FILE);
  Serial.println("[Config] Config cleared.");
}