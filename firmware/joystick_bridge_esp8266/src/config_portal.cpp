#include "config_portal.h"
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

namespace ConfigPortal {
  ESP8266WebServer server(80);
  
  const char* htmlPage = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Joystick Bridge Setup</title>
  <style>
    body { font-family: Arial; max-width: 500px; margin: 30px auto; padding: 20px; }
    input, button, select { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
    button { background: #007BFF; color: white; border: none; cursor: pointer; font-weight: bold; }
    button:hover { background: #0056b3; }
    h2 { color: #333; }
    .hint { font-size: 0.8em; color: #666; margin-top: -5px; margin-bottom: 15px; display: block; }
  </style>
</head>
<body>
  <h2>Joystick Bridge Setup</h2>
  <form action="/save" method="POST">
    <h3>WiFi Settings</h3>
    <input type="text" name="wifi_ssid" placeholder="WiFi SSID" required>
    <input type="password" name="wifi_pass" placeholder="WiFi Password (leave blank if none)">
    
    <h3>Backend Settings</h3>
    <span class="hint">E.g., confident-analysis-production-795d.up.railway.app</span>
    <input type="text" name="be_host" placeholder="Backend Host (No http://)" required>
    
    <span class="hint">Use 443 for Railway, 8000 for local</span>
    <input type="number" name="be_port" placeholder="Backend Port" value="443" required>
    
    <select name="be_tls">
      <option value="true" selected>Use TLS (https/wss) - Railway</option>
      <option value="false">No TLS (http/ws) - Local</option>
    </select>
    
    <h3>Joystick Identity (Optional)</h3>
    <input type="text" name="joy_id" placeholder="Joystick ID">
    <input type="password" name="joy_token" placeholder="Joystick Token">
    
    <button type="submit">Save & Reboot</button>
  </form>
</body>
</html>
)rawliteral";

  void handleRoot() {
    server.send(200, "text/html", htmlPage);
  }

  void handleSave() {
    AppConfig config;
    config.wifiSsid      = server.arg("wifi_ssid");
    config.wifiPassword  = server.arg("wifi_pass");
    config.backendHost   = server.arg("be_host");
    config.backendPort   = server.arg("be_port").toInt();
    config.backendTls    = server.arg("be_tls") == "true";
    config.joystickId    = server.arg("joy_id");
    config.joystickToken = server.arg("joy_token");
    config.valid         = true;
    
    saveConfig(config);
    
    String response = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Saved</title>
  <style>
    body { font-family: Arial; max-width: 500px; margin: 50px auto; padding: 20px; text-align: center; }
    h2 { color: #007BFF; }
  </style>
</head>
<body>
  <h2>Configuration Saved!</h2>
  <p>Joystick will reboot in 3 seconds...</p>
</body>
</html>
)rawliteral";
    
    server.send(200, "text/html", response);
    delay(3000);
    ESP.restart();
  }

  void start() {
    Serial.println("[Portal] Starting AP Config Portal...");
    
    WiFi.mode(WIFI_AP);
    WiFi.softAP("SmartCar-Joystick-Setup");
    
    IPAddress IP = WiFi.softAPIP();
    Serial.print("[Portal] AP IP address: ");
    Serial.println(IP);
    Serial.println("[Portal] Connect to WiFi 'SmartCar-Joystick-Setup'");
    Serial.print("[Portal] Then open http://");
    Serial.println(IP);
    
    server.on("/", HTTP_GET, handleRoot);
    server.on("/save", HTTP_POST, handleSave);
    server.begin();
    
    Serial.println("[Portal] Portal started. Blocking until configured...");
    
    while (true) {
      server.handleClient();
      delay(10);
    }
  }
}