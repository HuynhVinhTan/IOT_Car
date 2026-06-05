#pragma once
#include "app_config.h"
#include "button_input.h"

namespace JoystickClient {

  // Initialize WiFi and connection to backend
  void init(const AppConfig& config);

  // Send command over HTTP POST
  void sendCommand(ButtonInput::CommandState cmd);

  // Keep WebSocket alive and handle incoming events (like detection)
  void loop();
  
}