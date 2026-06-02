#include "command_parser.h"

#include <ArduinoJson.h>

ParsedJoystickCommand JoystickCommandParser::parseLine(
    const String& commandLine) const {
  ParsedJoystickCommand parsedCommand;

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

  if (strcmp(commandName, "START_PERSON_FOUND_ALERT") == 0) {
    parsedCommand.type = JoystickCommandType::StartPersonFoundAlert;
  } else if (strcmp(commandName, "STOP_PERSON_FOUND_ALERT") == 0) {
    parsedCommand.type = JoystickCommandType::StopPersonFoundAlert;
  } else if (strcmp(commandName, "PLAY_ALERT_ONCE") == 0) {
    parsedCommand.type = JoystickCommandType::PlayAlertOnce;
  } else if (strcmp(commandName, "SET_ALERT_ENABLED") == 0) {
    if (!commandDocument["enabled"].is<bool>()) {
      parsedCommand.errorMessage = "Invalid or missing enabled";
      return parsedCommand;
    }
    parsedCommand.type = JoystickCommandType::SetAlertEnabled;
    parsedCommand.alertEnabled = commandDocument["enabled"];
  } else {
    parsedCommand.errorMessage = "Unsupported command";
    return parsedCommand;
  }

  parsedCommand.valid = true;
  return parsedCommand;
}
