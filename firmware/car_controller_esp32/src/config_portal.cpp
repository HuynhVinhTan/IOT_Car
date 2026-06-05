#include "config_portal.h"
#include "app_config.h"
#include <WiFi.h>
#include <WebServer.h>

namespace ConfigPortal {
  WebServer server(80);
  
  const char* htmlPage = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Car Config</title>
  <style>
    body { font-family: Arial; max-width: 500px; margin: 50px auto; padding: 20px; }
    input, button { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
    button { background: #4CAF50; color: white; border: none; cursor: pointer; }
    button:hover { background: #45a049; }
    h2 { color: #333; }
  </style>
</head>
<body>
  <h2>Smart Car Configuration</h2>
  <form action="/save" method="POST">
    <h3>WiFi Settings</h3>
    <input type="text" name="wifi_ssid" placeholder="WiFi SSID" required>
    <input type="password" name="wifi_pass" placeholder="WiFi Password" required>
    
     <h3>Backend Settings</h3>
     <input type="text" name="be_host" placeholder="Backend Host (e.g., confident-analysis-production-795d.up.railway.app)" required>
     <input type="number" name="be_port" placeholder="Backend Port (e.g., 443)" value="443" required>
     <select name="be_tls">
       <option value="1" selected>true</option>
       <option value="0">false</option>
     </select>
    
    <h3>Car Identity</h3>
    <input type="text" name="car_id" placeholder="Car ID" required>
    <input type="password" name="car_token" placeholder="Car Token (optional)">
    
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
    config.wifiSsid = server.arg("wifi_ssid");
    config.wifiPassword = server.arg("wifi_pass");
    String beHost = server.arg("be_host");
    // Strip http:// or https:// if present
    if (beHost.startsWith("http://")) {
      beHost = beHost.substring(7);
      Serial.println("WARNING: Stripped http:// from backend host");
    } else if (beHost.startsWith("https://")) {
      beHost = beHost.substring(8);
      Serial.println("WARNING: Stripped https:// from backend host");
    }
    config.backendHost = beHost;
    config.backendPort = server.arg("be_port").toInt();
    config.backendTls = server.arg("be_tls") == "1";
    config.carId = server.arg("car_id");
    config.carToken = server.arg("car_token");
    config.valid = true;
    
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
    h2 { color: #4CAF50; }
  </style>
</head>
<body>
  <h2>Configuration Saved!</h2>
  <p>ESP32 will reboot in 3 seconds...</p>
</body>
</html>
)rawliteral";
    
    server.send(200, "text/html", response);
    delay(3000);
    ESP.restart();
  }

  void start() {
    Serial.println("Starting Config Portal...");
    
    WiFi.mode(WIFI_AP);
    WiFi.softAP("SmartCar-Setup");
    
    IPAddress IP = WiFi.softAPIP();
    Serial.print("AP IP address: ");
    Serial.println(IP);
    Serial.println("Connect to WiFi 'SmartCar-Setup' (password: 12345678)");
    Serial.print("Then open http://");
    Serial.println(IP);
    
    server.on("/", handleRoot);
    server.on("/save", HTTP_POST, handleSave);
    server.on("/reset", []() {
      Preferences prefs;
      prefs.begin("config", false);
      prefs.clear();
      prefs.end();
      server.send(200, "text/plain", "Config cleared. Rebooting...");
      delay(1000);
      ESP.restart();
    });
    server.begin();
    
    Serial.println("Config Portal started. Waiting for configuration...");
    
    while (true) {
      server.handleClient();
      delay(10);
    }
  }
}