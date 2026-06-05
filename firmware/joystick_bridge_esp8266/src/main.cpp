#include <Arduino.h>
#include "pin_config.h"
#include "app_config.h"
#include "config_portal.h"
#include "button_input.h"
#include "joystick_client.h"
#include "alert_output.h"

AppConfig currentConfig;
unsigned long lastCommandSendTime = 0;
ButtonInput::CommandState lastCommand = ButtonInput::CMD_STOP;
bool wasMoving = false;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n--- Joystick Bridge ESP8266 Starting ---");

  // Initialize hardware pins
  ButtonInput::init();
  AlertOutput::init();

  // Load config
  loadConfig(currentConfig);
  printConfig(currentConfig);

  // If no valid config, enter setup portal
  if (!currentConfig.valid) {
    ConfigPortal::start();
    // Portal will reboot on save, so we won't reach here
  }

  // Initialize WiFi and Backend Connection
  JoystickClient::init(currentConfig);
}

void loop() {
  // Update WebSocket and Alert pattern
  JoystickClient::loop();
  AlertOutput::update();

  // Read button state
  ButtonInput::CommandState currentCmd = ButtonInput::readState();
  unsigned long now = millis();

  // Send command logic
  if (currentCmd != ButtonInput::CMD_STOP) {
    // We are holding a direction
    if (now - lastCommandSendTime >= COMMAND_SEND_INTERVAL_MS) {
      JoystickClient::sendCommand(currentCmd);
      lastCommandSendTime = now;
      wasMoving = true;
    }
  } else {
    // All buttons released
    if (wasMoving) {
      // Send STOP once immediately when released
      JoystickClient::sendCommand(ButtonInput::CMD_STOP);
      wasMoving = false;
      lastCommandSendTime = now;
    }
  }

  // Yield to allow background tasks to run
  yield();
}