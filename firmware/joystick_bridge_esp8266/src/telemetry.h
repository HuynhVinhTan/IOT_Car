#pragma once

#include <Arduino.h>
#include "joystick_types.h"

class JoystickTelemetryPublisher {
 public:
  void begin(Stream& outputStream);
  void publish(const JoystickReading& joystickReading);
  void publishCommandAck(const String& commandName, bool success,
                         const String& message);
  void publishRemoteButtonEvent(const String& eventName,
                                unsigned long timestampMs);
  void publishRemoteRouteEvent(const RouteButtonEvent& event);


 private:
  Stream* outputStream_ = nullptr;
};
