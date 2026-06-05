#pragma once

#include <Arduino.h>

// ---------------------------------------------------------------------------
// AppConfig – runtime configuration stored in NVS (Preferences)
// ---------------------------------------------------------------------------
struct AppConfig {
  String wifiSsid;
  String wifiPassword;

  String backendHost;
  uint16_t backendPort;
  bool backendTls;

  String cameraId;
  String cameraToken;

  uint32_t frameIntervalMs;
  int jpegQuality;

  // New fields
  String frameSize;        // "QQVGA", "QVGA", "VGA"
  uint32_t xclkFreqHz;     // 10000000 hoặc 20000000
  int fbCount;             // 1 hoặc 2
  String grabMode;         // "WHEN_EMPTY" hoặc "LATEST"
  bool cameraDiagEnabled;  // true/false

  bool valid;  // populated by isAppConfigValid()
};

// ---------------------------------------------------------------------------
// NVS helpers
// ---------------------------------------------------------------------------

/// Load config from NVS into `config`. Returns true if NVS had saved data.
bool loadAppConfig(AppConfig &config);

/// Persist config to NVS. Returns true on success.
bool saveAppConfig(const AppConfig &config);

/// Erase all config keys from NVS.
void clearAppConfig();

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

/// Validate fields and set config.valid accordingly. Returns config.valid.
bool isAppConfigValid(AppConfig &config);

// ---------------------------------------------------------------------------
// Safe printing (masks password & token)
// ---------------------------------------------------------------------------

/// Print config to Serial with sensitive fields masked.
void printSafeAppConfig(const AppConfig &config);