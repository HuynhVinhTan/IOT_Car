#include "config_portal.h"
#include "app_config.h"

#include <WiFi.h>
#include <WebServer.h>

// ---------------------------------------------------------------------------
// HTML form served at /
// ---------------------------------------------------------------------------
static const char HTML_FORM[] PROGMEM = R"rawliteral(
<!DOCTYPE html><html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SmartCar Setup</title>
<style>
body{font-family:sans-serif;max-width:420px;margin:40px auto;padding:0 12px}
label{display:block;margin-top:10px;font-weight:bold}
input,select{width:100%;padding:6px;box-sizing:border-box}
button{margin-top:18px;padding:10px 20px;font-size:16px;cursor:pointer}
.warn{color:#c00;margin-top:12px}
</style></head><body>
<h2>&#128663; SmartCar Config</h2>
<form method="POST" action="/save">

<label>WiFi SSID</label>
<input name="wifi_ssid" required>

<label>WiFi Password</label>
<input name="wifi_pass" type="password" required>

<label>Backend Host</label>
<input name="ws_host" required>

<label>Backend Port</label>
<input name="ws_port" type="number" value="443" min="1" max="65535">

<label>Backend TLS</label>
<select name="ws_tls"><option value="1" selected>true</option><option value="0">false</option></select>

<label>Camera ID</label>
<input name="cam_id" value="car_front_camera" required>

<label>Camera Token</label>
<input name="cam_token" type="password" required>

<label>Frame Interval (ms)</label>
<input name="frame_ms" type="number" value="64" min="50" max="1000">

<label>JPEG Quality (6-20, lower=better)</label>
<input name="jpeg_q" type="number" value="8" min="6" max="20">

<button type="submit">Save & Restart</button>
</form>

<hr>
<form method="POST" action="/reset">
<button type="submit" style="background:#c00;color:#fff">Reset Config</button>
</form>
</body></html>
)rawliteral";

// ---------------------------------------------------------------------------
// Portal implementation
// ---------------------------------------------------------------------------
void startConfigPortal(const char *apSsid) {
  Serial.println("[PORTAL] Starting config portal AP...");

  WiFi.disconnect(true);
  WiFi.mode(WIFI_AP);
  WiFi.softAP(apSsid);
  delay(500);

  Serial.print("[PORTAL] AP SSID : ");
  Serial.println(apSsid);
  Serial.print("[PORTAL] AP IP   : ");
  Serial.println(WiFi.softAPIP());

  WebServer server(80);

  // --- GET / ---
  server.on("/", HTTP_GET, [&server]() {
    server.send(200, "text/html", HTML_FORM);
  });

  // --- POST /save ---
  server.on("/save", HTTP_POST, [&server]() {
    AppConfig cfg;
    cfg.wifiSsid       = server.arg("wifi_ssid");
    cfg.wifiPassword    = server.arg("wifi_pass");
    cfg.backendHost     = server.arg("ws_host");
    cfg.backendPort     = (uint16_t)server.arg("ws_port").toInt();
    cfg.backendTls      = server.arg("ws_tls") == "1";
    cfg.cameraId        = server.arg("cam_id");
    cfg.cameraToken     = server.arg("cam_token");
    cfg.frameIntervalMs = (uint32_t)server.arg("frame_ms").toInt();
    cfg.jpegQuality     = server.arg("jpeg_q").toInt();

    if (!isAppConfigValid(cfg)) {
      server.send(400, "text/html",
        "<html><body><h2>Invalid config</h2>"
        "<p>Please check all fields and try again.</p>"
        "<a href='/'>Back</a></body></html>");
      return;
    }

    saveAppConfig(cfg);
    printSafeAppConfig(cfg);

    server.send(200, "text/html",
      "<html><body><h2>Config saved!</h2>"
      "<p>Restarting in 3 seconds...</p></body></html>");

    delay(3000);
    ESP.restart();
  });

  // --- POST /reset ---
  server.on("/reset", HTTP_POST, [&server]() {
    clearAppConfig();
    server.send(200, "text/html",
      "<html><body><h2>Config cleared!</h2>"
      "<p>Restarting in 3 seconds...</p></body></html>");
    delay(3000);
    ESP.restart();
  });

  server.begin();
  Serial.println("[PORTAL] Web server started – waiting for config at http://192.168.4.1");

  // Blocking loop – portal runs until user saves config (triggers restart)
  while (true) {
    server.handleClient();
    delay(2);
  }
}