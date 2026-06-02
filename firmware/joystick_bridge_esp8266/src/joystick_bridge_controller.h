#pragma once

#include <Arduino.h>
#include "alert_siren.h"
#include "command_parser.h"
#include "joystick_reader.h"
#include "remote_mode_button.h"
#include "telemetry.h"
#include "route_button_controller.h"

class JoystickBridgeController {
 public:
  void begin();
  void update();

 private:
  void readSerialCommands();
  void applyParsedCommand(const ParsedJoystickCommand& parsedCommand,
                          unsigned long currentTimeMs);

  JoystickReader joystickReader_;
  RemoteModeButton remoteModeButton_;
  RouteButtonController routeButtonController_;
  AlertSiren alertSiren_;
  JoystickCommandParser commandParser_;
  JoystickTelemetryPublisher telemetryPublisher_;
  String serialCommandBuffer_;
  unsigned long lastTelemetryMs_ = 0;
  bool lastJoystickButtonPressed_ = false;
};
