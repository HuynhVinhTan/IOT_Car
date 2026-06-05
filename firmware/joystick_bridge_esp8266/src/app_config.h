#pragma once
#include <Arduino.h>

struct AppConfig {
  String wifiSsid;
  String wifiPassword;
  String backendHost;
  uint16_t backendPort;
  bool backendTls;
  String joystickId;
  String joystickToken;
  bool valid;
};

void loadConfig(AppConfig &config);
void saveConfig(const AppConfig &config);
bool isAppConfigValid(const AppConfig &config);
void printConfig(const AppConfig &config);
void clearConfig();