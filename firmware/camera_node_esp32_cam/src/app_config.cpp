#include "app_config.h"
#include <Preferences.h>

// NVS namespace
static const char *NVS_NAMESPACE = "smartcar";

// Load
bool loadAppConfig(AppConfig &config) {
  Preferences prefs;

  if (!prefs.begin(NVS_NAMESPACE, true)) {  // read-only
    Serial.println("[CFG] NVS open failed");
    config.valid = false;
    return false;
  }

  config.wifiSsid       = prefs.getString("wifi_ssid", "");
  config.wifiPassword   = prefs.getString("wifi_pass", "");
  config.backendHost    = prefs.getString("ws_host", "");
  config.backendPort    = prefs.getUShort("ws_port", 443);
  config.backendTls     = prefs.getBool("ws_tls", true);
  config.cameraId       = prefs.getString("cam_id", "");
  config.cameraToken    = prefs.getString("cam_token", "");
  config.frameIntervalMs = prefs.getULong("frame_ms", 180);
  config.jpegQuality    = prefs.getInt("jpeg_q", 12);
  
  config.frameSize      = prefs.getString("frame_size", "QVGA");
  config.xclkFreqHz     = prefs.getULong("xclk_hz", 10000000);
  config.fbCount        = prefs.getInt("fb_count", 1);
  config.grabMode       = prefs.getString("grab_mode", "WHEN_EMPTY");
  config.cameraDiagEnabled = prefs.getBool("cam_diag", false);

  prefs.end();

  return isAppConfigValid(config);
}

// Save
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
  
  prefs.putString("frame_size", config.frameSize);
  prefs.putULong("xclk_hz",     config.xclkFreqHz);
  prefs.putInt("fb_count",      config.fbCount);
  prefs.putString("grab_mode",  config.grabMode);
  prefs.putBool("cam_diag",     config.cameraDiagEnabled);

  prefs.end();
  Serial.println("[CFG] Config saved to NVS");
  return true;
}

// Clear
void clearAppConfig() {
  Preferences prefs;
  prefs.begin(NVS_NAMESPACE, false);
  prefs.clear();
  prefs.end();
  Serial.println("[CFG] Config cleared from NVS");
}

// Validation
bool isAppConfigValid(AppConfig &config) {
  config.valid = true;

  if (config.wifiSsid.length() == 0) config.valid = false;
  if (config.backendHost.length() == 0) config.valid = false;
  if (config.backendPort == 0 || config.backendPort > 65535) config.valid = false;
  if (config.cameraId.length() == 0) config.valid = false;
  if (config.cameraToken.length() == 0) config.valid = false;
  
  if (config.frameIntervalMs < 100 || config.frameIntervalMs > 1000) config.valid = false;
  if (config.jpegQuality < 6 || config.jpegQuality > 30) config.valid = false;
  
  if (config.frameSize != "QQVGA" && config.frameSize != "QVGA" && config.frameSize != "VGA") config.valid = false;
  if (config.xclkFreqHz != 10000000 && config.xclkFreqHz != 20000000) config.valid = false;
  if (config.fbCount != 1 && config.fbCount != 2) config.valid = false;
  if (config.grabMode != "WHEN_EMPTY" && config.grabMode != "LATEST") config.valid = false;

  return config.valid;
}

// Safe print (mask secrets)
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
  Serial.printf("  frame_size     : %s\n", config.frameSize.c_str());
  Serial.printf("  xclk_hz        : %u\n", config.xclkFreqHz);
  Serial.printf("  fb_count       : %d\n", config.fbCount);
  Serial.printf("  grab_mode      : %s\n", config.grabMode.c_str());
  Serial.printf("  camera_diag    : %s\n", config.cameraDiagEnabled ? "true" : "false");
  Serial.printf("  valid          : %s\n", config.valid ? "YES" : "NO");
  Serial.println("=================");
}