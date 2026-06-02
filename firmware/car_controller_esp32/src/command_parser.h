#pragma once

#include <Arduino.h>
#include "car_types.h"

enum class CommandType {
  Unknown,
  SetMode,
  RemoteDrive,
  RemoteStop,
  StartRecord,
  StopRecord,
  ClearPath,
  StartAuto,
  StopAuto,
  EmergencyStop,
  ResetEmergency,
  PersonDetected,
  PersonLost
};

struct ParsedCommand {
  bool valid = false;
  CommandType type = CommandType::Unknown;
  String commandName;
  DriveMode requestedMode = DriveMode::Idle;
  int leftMotorSpeed = 0;
  int rightMotorSpeed = 0;
  bool personDetected = false;
  String errorMessage;
};

class CommandParser {
 public:
  ParsedCommand parseLine(const String& commandLine) const;
};
