#include "app_config.h"

void loadConfig(AppConfig &config) {
  Preferences prefs;
  prefs.begin("config", true);
  config.wifiSsid = prefs.getString("wifi_ssid", "");
  config.wifiPassword = prefs.getString("wifi_pass", "");
  config.backendHost = prefs.getString("be_host", "");
  config.backendPort = prefs.getUShort("be_port", 8000);
  config.backendTls = prefs.getBool("be_tls", false);
  config.carId = prefs.getString("car_id", "");
  config.carToken = prefs.getString("car_token", "");
  prefs.end();
  config.valid = isAppConfigValid(config);
}

void saveConfig(const AppConfig &config) {
  Preferences prefs;
  prefs.begin("config", false);
  prefs.putString("wifi_ssid", config.wifiSsid);
  prefs.putString("wifi_pass", config.wifiPassword);
  prefs.putString("be_host", config.backendHost);
  prefs.putUShort("be_port", config.backendPort);
  prefs.putBool("be_tls", config.backendTls);
  prefs.putString("car_id", config.carId);
  prefs.putString("car_token", config.carToken);
  prefs.end();
}

bool isAppConfigValid(const AppConfig &config) {
  return config.wifiSsid.length() > 0 && 
         config.backendHost.length() > 0 && 
         config.backendPort > 0 &&
         config.carId.length() > 0;
}

void printConfig(const AppConfig &config) {
  Serial.println("--- Current Config ---");
  Serial.printf("WiFi SSID: %s\n", config.wifiSsid.c_str());
  Serial.printf("WiFi Pass: %s\n", config.wifiPassword.length() > 0 ? "******" : "");
  Serial.printf("Backend: %s:%d (TLS: %s)\n", config.backendHost.c_str(), config.backendPort, config.backendTls ? "true" : "false");
  Serial.printf("Car ID: %s\n", config.carId.c_str());
  Serial.printf("Token: %s\n", config.carToken.length() > 0 ? "******" : "");
  Serial.printf("Valid: %s\n", config.valid ? "true" : "false");
}