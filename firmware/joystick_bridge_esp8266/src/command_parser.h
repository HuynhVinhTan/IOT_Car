#pragma once

#include <Arduino.h>

enum class JoystickCommandType {
  Unknown,
  StartPersonFoundAlert,
  StopPersonFoundAlert,
  PlayAlertOnce,
  SetAlertEnabled
};

struct ParsedJoystickCommand {
  bool valid = false;
  JoystickCommandType type = JoystickCommandType::Unknown;
  String commandName;
  bool alertEnabled = true;
  String errorMessage;
};

class JoystickCommandParser {
 public:
  ParsedJoystickCommand parseLine(const String& commandLine) const;
};
