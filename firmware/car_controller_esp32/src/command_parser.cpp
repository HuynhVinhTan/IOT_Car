#include "command_parser.h"

#include <ArduinoJson.h>

ParsedCommand CommandParser::parseLine(const String& commandLine) const {
  ParsedCommand parsedCommand;

  JsonDocument commandDocument;
  const DeserializationError deserializeError =
      deserializeJson(commandDocument, commandLine);

  if (deserializeError) {
    parsedCommand.commandName = "UNKNOWN";
    parsedCommand.errorMessage = "Invalid JSON command";
    return parsedCommand;
  }

  const char* commandName = commandDocument["command"];
  if (commandName == nullptr) {
    parsedCommand.commandName = "UNKNOWN";
    parsedCommand.errorMessage = "Missing command field";
    return parsedCommand;
  }

  parsedCommand.commandName = commandName;

  if (strcmp(commandName, "SET_MODE") == 0) {
    const char* requestedModeText = commandDocument["mode"];
    DriveMode requestedMode = DriveMode::Idle;
    if (!parseDriveMode(requestedModeText, requestedMode)) {
      parsedCommand.errorMessage = "Invalid or missing mode";
      return parsedCommand;
    }
    parsedCommand.type = CommandType::SetMode;
    parsedCommand.requestedMode = requestedMode;
  } else if (strcmp(commandName, "REMOTE_DRIVE") == 0) {
    if (!commandDocument["left_motor_speed"].is<int>() ||
        !commandDocument["right_motor_speed"].is<int>()) {
      parsedCommand.errorMessage = "Invalid or missing motor speed";
      return parsedCommand;
    }
    parsedCommand.type = CommandType::RemoteDrive;
    parsedCommand.leftMotorSpeed = commandDocument["left_motor_speed"];
    parsedCommand.rightMotorSpeed = commandDocument["right_motor_speed"];
  } else if (strcmp(commandName, "REMOTE_STOP") == 0 ||
             strcmp(commandName, "STOP") == 0) {
    parsedCommand.type = CommandType::RemoteStop;
  } else if (strcmp(commandName, "START_RECORD") == 0) {
    parsedCommand.type = CommandType::StartRecord;
  } else if (strcmp(commandName, "STOP_RECORD") == 0) {
    parsedCommand.type = CommandType::StopRecord;
  } else if (strcmp(commandName, "CLEAR_PATH") == 0) {
    parsedCommand.type = CommandType::ClearPath;
  } else if (strcmp(commandName, "START_AUTO") == 0 ||
             strcmp(commandName, "START_AUTO_SEARCH") == 0) {
    parsedCommand.type = CommandType::StartAuto;
  } else if (strcmp(commandName, "STOP_AUTO") == 0 ||
             strcmp(commandName, "STOP_MISSION") == 0) {
    parsedCommand.type = CommandType::StopAuto;
  } else if (strcmp(commandName, "RETURN_HOME") == 0) {
    parsedCommand.type = CommandType::SetMode;
    parsedCommand.requestedMode = DriveMode::ReturnHome;
  } else if (strcmp(commandName, "EMERGENCY_STOP") == 0) {
    parsedCommand.type = CommandType::EmergencyStop;
  } else if (strcmp(commandName, "RESET_EMERGENCY") == 0) {
    parsedCommand.type = CommandType::ResetEmergency;
  } else if (strcmp(commandName, "PERSON_DETECTED") == 0) {
    if (!commandDocument["detected"].is<bool>()) {
      parsedCommand.errorMessage = "Invalid or missing detected";
      return parsedCommand;
    }
    parsedCommand.type = CommandType::PersonDetected;
    parsedCommand.personDetected = commandDocument["detected"];
  } else if (strcmp(commandName, "PERSON_LOST") == 0) {
    parsedCommand.type = CommandType::PersonLost;
    parsedCommand.personDetected = false;
  } else {
    parsedCommand.errorMessage = "Unsupported command";
    return parsedCommand;
  }

  parsedCommand.valid = true;
  return parsedCommand;
}
