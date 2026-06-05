#pragma once
#include <Arduino.h>
#include <Preferences.h>

struct AppConfig {
  String wifiSsid;
  String wifiPassword;
  String backendHost;
  uint16_t backendPort;
  bool backendTls;
  String carId;
  String carToken;
  bool valid;
};

void loadConfig(AppConfig &config);
void saveConfig(const AppConfig &config);
bool isAppConfigValid(const AppConfig &config);
void printConfig(const AppConfig &config);