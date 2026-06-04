#include "serial_cli.h"

#if defined(ENABLE_SERIAL_CLI) && ENABLE_SERIAL_CLI == 1

#include <Arduino.h>

// ---------------------------------------------------------------------------
// Internal state
// ---------------------------------------------------------------------------
static String s_lineBuffer;

// Pending changes accumulate here; written to NVS on "save" command
static AppConfig *s_cfg = nullptr;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
static void printHelp() {
  Serial.println("=== Serial CLI (dev mode) ===");
  Serial.println("  show");
  Serial.println("  reset-config");
  Serial.println("  reboot");
  Serial.println("  set-wifi <ssid> <password>");
  Serial.println("  set-backend <host> <port> <tls:true|false>");
  Serial.println("  set-camera <camera_id> <token>");
  Serial.println("  set-stream <frame_interval_ms> <jpeg_quality>");
  Serial.println("  save");
  Serial.println("  help");
  Serial.println("==============================");
}

static void handleLine(const String &line, AppConfig &cfg) {
  String l = line;
  l.trim();
  if (l.length() == 0) return;

  // Split into tokens
  int sp0 = l.indexOf(' ');
  String cmd = (sp0 < 0) ? l : l.substring(0, sp0);
  String rest = (sp0 < 0) ? "" : l.substring(sp0 + 1);
  rest.trim();

  if (cmd == "help") {
    printHelp();

  } else if (cmd == "show") {
    printSafeAppConfig(cfg);

  } else if (cmd == "reset-config") {
    clearAppConfig();
    Serial.println("[CLI] Config cleared. Rebooting...");
    delay(500);
    ESP.restart();

  } else if (cmd == "reboot") {
    Serial.println("[CLI] Rebooting...");
    delay(300);
    ESP.restart();

  } else if (cmd == "set-wifi") {
    int sp1 = rest.indexOf(' ');
    if (sp1 < 0) {
      Serial.println("[CLI] Usage: set-wifi <ssid> <password>");
      return;
    }
    cfg.wifiSsid = rest.substring(0, sp1);
    cfg.wifiPassword = rest.substring(sp1 + 1);
    // Do NOT log password
    Serial.printf("[CLI] wifi_ssid set to: %s  (password updated)\n", cfg.wifiSsid.c_str());

  } else if (cmd == "set-backend") {
    // set-backend <host> <port> <tls:true|false>
    int sp1 = rest.indexOf(' ');
    if (sp1 < 0) { Serial.println("[CLI] Usage: set-backend <host> <port> <tls>"); return; }
    String host = rest.substring(0, sp1);
    rest = rest.substring(sp1 + 1);
    rest.trim();
    int sp2 = rest.indexOf(' ');
    if (sp2 < 0) { Serial.println("[CLI] Usage: set-backend <host> <port> <tls>"); return; }
    uint16_t port = (uint16_t)rest.substring(0, sp2).toInt();
    String tlsStr = rest.substring(sp2 + 1);
    tlsStr.trim();
    bool tls = (tlsStr == "true" || tlsStr == "1");
    cfg.backendHost = host;
    cfg.backendPort = port;
    cfg.backendTls  = tls;
    Serial.printf("[CLI] backend: host=%s port=%u tls=%s\n",
                  cfg.backendHost.c_str(), cfg.backendPort,
                  cfg.backendTls ? "true" : "false");

  } else if (cmd == "set-camera") {
    int sp1 = rest.indexOf(' ');
    if (sp1 < 0) { Serial.println("[CLI] Usage: set-camera <camera_id> <token>"); return; }
    cfg.cameraId = rest.substring(0, sp1);
    cfg.cameraToken = rest.substring(sp1 + 1);
    // Do NOT log token
    Serial.printf("[CLI] camera_id set to: %s  (token updated)\n", cfg.cameraId.c_str());

  } else if (cmd == "set-stream") {
    int sp1 = rest.indexOf(' ');
    if (sp1 < 0) { Serial.println("[CLI] Usage: set-stream <frame_ms> <jpeg_quality>"); return; }
    uint32_t ms  = (uint32_t)rest.substring(0, sp1).toInt();
    int      q   = rest.substring(sp1 + 1).toInt();
    cfg.frameIntervalMs = ms;
    cfg.jpegQuality     = q;
    Serial.printf("[CLI] stream: frame_ms=%u jpeg_q=%d\n", ms, q);

  } else if (cmd == "save") {
    if (!isAppConfigValid(cfg)) {
      Serial.println("[CLI] Config invalid – fix errors before saving");
      printSafeAppConfig(cfg);
      return;
    }
    saveAppConfig(cfg);
    Serial.println("[CLI] Saved. Reboot to apply.");

  } else {
    Serial.printf("[CLI] Unknown command: %s  (type 'help')\n", cmd.c_str());
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------
void serialCliBegin(AppConfig &config) {
  s_cfg = &config;
  Serial.println("[CLI] Serial CLI ready (dev mode). Type 'help'.");
}

void serialCliTick(AppConfig &config) {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      handleLine(s_lineBuffer, config);
      s_lineBuffer = "";
    } else {
      s_lineBuffer += c;
      // Guard against runaway buffer
      if (s_lineBuffer.length() > 256) s_lineBuffer = "";
    }
  }
}

#endif  // ENABLE_SERIAL_CLI