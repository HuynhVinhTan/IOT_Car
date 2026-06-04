#include "app_config.h"
#include <Preferences.h>

// NVS namespace
static const char *NVS_NAMESPACE = "smartcar";

// ---------------------------------------------------------------------------
// Load
// ---------------------------------------------------------------------------
bool loadAppConfig(AppConfig &config) {
  Preferences prefs;
  prefs.begin(NVS_NAMESPACE, true);  // read-only

  config.wifiSsid       = prefs.getString("wifi_ssid", "");
  config.wifiPassword    = prefs.getString("wifi_pass", "");
  config.backendHost     = prefs.getString("ws_host", "");
  config.backendPort     = prefs.getUShort("ws_port", 443);
  config.backendTls      = prefs.getBool("ws_tls", true);
  config.cameraId        = prefs.getString("cam_id", "");
  config.cameraToken     = prefs.getString("cam_token", "");
  config.frameIntervalMs = prefs.getULong("frame_ms", 64);
  config.jpegQuality     = prefs.getInt("jpeg_q", 8);

  prefs.end();

  // Check if anything was actually stored
  bool hasData = config.wifiSsid.length() > 0;
  return hasData;
}

// ---------------------------------------------------------------------------
// Save
// ---------------------------------------------------------------------------
bool saveAppConfig(const AppConfig &config) {
  Preferences prefs;
  if (!prefs.begin(NVS_NAMESPACE, false)) {  // read-write
    Serial.println("[CFG] NVS open failed");
    return false;
  }

  prefs.putString("wifi_ssid",  config.wifiSsid);
  prefs.putString("wifi_pass",  config.wifiPassword);
  prefs.putString("ws_host",    config.backendHost);
  prefs.putUShort("ws_port",    config.backendPort);
  prefs.putBool("ws_tls",       config.backendTls);
  prefs.putString("cam_id",     config.cameraId);
  prefs.putString("cam_token",  config.cameraToken);
  prefs.putULong("frame_ms",    config.frameIntervalMs);
  prefs.putInt("jpeg_q",        config.jpegQuality);

  prefs.end();
  Serial.println("[CFG] Config saved to NVS");
  return true;
}

// ---------------------------------------------------------------------------
// Clear
// ---------------------------------------------------------------------------
void clearAppConfig() {
  Preferences prefs;
  prefs.begin(NVS_NAMESPACE, false);
  prefs.clear();
  prefs.end();
  Serial.println("[CFG] Config cleared from NVS");
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------
bool isAppConfigValid(AppConfig &config) {
  config.valid = true;

  if (config.wifiSsid.length() == 0) {
    config.valid = false;
  }
  if (config.backendHost.length() == 0) {
    config.valid = false;
  }
  if (config.backendPort == 0 || config.backendPort > 65535) {
    config.valid = false;
  }
  if (config.cameraId.length() == 0) {
    config.valid = false;
  }
  if (config.cameraToken.length() == 0) {
    config.valid = false;
  }
  // Clamp frame interval to safe range
  if (config.frameIntervalMs < 50 || config.frameIntervalMs > 1000) {
    config.valid = false;
  }
  // JPEG quality: ESP32-CAM uses 0-63, lower = better quality.
  // Practical range for streaming: 6–20
  if (config.jpegQuality < 6 || config.jpegQuality > 20) {
    config.valid = false;
  }

  return config.valid;
}

// ---------------------------------------------------------------------------
// Safe print (mask secrets)
// ---------------------------------------------------------------------------
static String maskSecret(const String &s) {
  if (s.length() <= 2) return "***";
  return s.substring(0, 1) + String("******") + s.substring(s.length() - 1);
}

void printSafeAppConfig(const AppConfig &config) {
  Serial.println("=== AppConfig ===");
  Serial.printf("  wifi_ssid      : %s\n", config.wifiSsid.c_str());
  Serial.printf("  wifi_pass      : %s\n", maskSecret(config.wifiPassword).c_str());
  Serial.printf("  backend_host   : %s\n", config.backendHost.c_str());
  Serial.printf("  backend_port   : %u\n", config.backendPort);
  Serial.printf("  backend_tls    : %s\n", config.backendTls ? "true" : "false");
  Serial.printf("  camera_id      : %s\n", config.cameraId.c_str());
  Serial.printf("  camera_token   : %s\n", maskSecret(config.cameraToken).c_str());
  Serial.printf("  frame_interval : %u ms\n", config.frameIntervalMs);
  Serial.printf("  jpeg_quality   : %d\n", config.jpegQuality);
  Serial.printf("  valid          : %s\n", config.valid ? "YES" : "NO");
  Serial.println("=================");
}