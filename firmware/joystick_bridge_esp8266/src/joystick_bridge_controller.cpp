#include "joystick_bridge_controller.h"

void JoystickBridgeController::begin() {
  Serial.begin(SERIAL_BAUD_RATE);
  serialCommandBuffer_.reserve(MAX_SERIAL_COMMAND_LENGTH);
  joystickReader_.begin();
  remoteModeButton_.begin();
  routeButtonController_.begin();
  alertSiren_.begin();
  telemetryPublisher_.begin(Serial);
}

void JoystickBridgeController::update() {
  const unsigned long currentTimeMs = millis();

  readSerialCommands();
  alertSiren_.update(currentTimeMs);
  remoteModeButton_.update(currentTimeMs);

  if (remoteModeButton_.wasShortPressed()) {
    telemetryPublisher_.publishRemoteButtonEvent("mode_button_short_press",
                                                 currentTimeMs);
  }
  if (remoteModeButton_.wasLongPressed()) {
    telemetryPublisher_.publishRemoteButtonEvent("mode_button_long_press",
                                                 currentTimeMs);
  }

  routeButtonController_.update(currentTimeMs);
  while (routeButtonController_.hasEvent()) {
    RouteButtonEvent event = routeButtonController_.consumeEvent();
    telemetryPublisher_.publishRemoteRouteEvent(event);
  }

  joystickReader_.update(currentTimeMs);
  JoystickReading joystickReading = joystickReader_.getState();

  // Joystick center button maps to route cancel on release.
  if (joystickReading.joystickButtonPressed && !lastJoystickButtonPressed_) {
    // Just pressed
    lastJoystickButtonPressed_ = true;
  } else if (!joystickReading.joystickButtonPressed && lastJoystickButtonPressed_) {
    // Released (short press equivalent)
    RouteButtonEvent cancelEvent;
    cancelEvent.type = RouteButtonEventType::CancelSegment;
    cancelEvent.timestampMs = currentTimeMs;
    telemetryPublisher_.publishRemoteRouteEvent(cancelEvent);
    lastJoystickButtonPressed_ = false;
  }

  // Heading hint advisory is inferred by the backend from joystick telemetry.
  // Do not publish separate route events here; that would duplicate telemetry
  // and can flood the serial link during continuous joystick movement.
  if (!joystickReading.deadzoneApplied && (abs(joystickReading.normalizedX) > 0.05 || abs(joystickReading.normalizedY) > 0.05)) {
    // Reserved for a future edge-triggered advisory if telemetry alone is not enough.
  }

  if (currentTimeMs - lastTelemetryMs_ < JOYSTICK_TELEMETRY_INTERVAL_MS) {
    return;
  }

  joystickReading.alertSirenActive = alertSiren_.isActive();
  joystickReading.alertEnabled = alertSiren_.isEnabled();
  joystickReading.remoteModeButtonPressed = remoteModeButton_.isPressed();
  telemetryPublisher_.publish(joystickReading);
  lastTelemetryMs_ = currentTimeMs;
}

void JoystickBridgeController::readSerialCommands() {
  while (Serial.available() > 0) {
    const char incomingCharacter = static_cast<char>(Serial.read());

    if (incomingCharacter == '\n') {
      serialCommandBuffer_.trim();
      if (serialCommandBuffer_.length() > 0) {
        const ParsedJoystickCommand parsedCommand =
            commandParser_.parseLine(serialCommandBuffer_);
        applyParsedCommand(parsedCommand, millis());
      }
      serialCommandBuffer_ = "";
      continue;
    }

    if (incomingCharacter == '\r') {
      continue;
    }

    if (serialCommandBuffer_.length() >= MAX_SERIAL_COMMAND_LENGTH) {
      telemetryPublisher_.publishCommandAck(
          "UNKNOWN", false, "Serial command exceeded maximum length");
      serialCommandBuffer_ = "";
      continue;
    }

    serialCommandBuffer_ += incomingCharacter;
  }
}

void JoystickBridgeController::applyParsedCommand(
    const ParsedJoystickCommand& parsedCommand, unsigned long currentTimeMs) {
  if (!parsedCommand.valid) {
    telemetryPublisher_.publishCommandAck(parsedCommand.commandName, false,
                                          parsedCommand.errorMessage);
    return;
  }

  switch (parsedCommand.type) {
    case JoystickCommandType::StartPersonFoundAlert:
      alertSiren_.start();
      telemetryPublisher_.publishCommandAck(parsedCommand.commandName, true,
                                            "Person found alert started");
      break;
    case JoystickCommandType::StopPersonFoundAlert:
      alertSiren_.stop();
      telemetryPublisher_.publishCommandAck(parsedCommand.commandName, true,
                                            "Person found alert stopped");
      break;
    case JoystickCommandType::PlayAlertOnce:
      alertSiren_.playOnce(currentTimeMs);
      telemetryPublisher_.publishCommandAck(parsedCommand.commandName, true,
                                            "Alert played once");
      break;
    case JoystickCommandType::SetAlertEnabled:
      alertSiren_.setEnabled(parsedCommand.alertEnabled);
      telemetryPublisher_.publishCommandAck(parsedCommand.commandName, true,
                                            "Alert enabled state updated");
      break;
    case JoystickCommandType::Unknown:
    default:
      telemetryPublisher_.publishCommandAck(parsedCommand.commandName, false,
                                            "Unsupported command");
      break;
  }
}
