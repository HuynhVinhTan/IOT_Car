#pragma once

#include <Arduino.h>
#include "car_types.h"

class TelemetryPublisher {
 public:
  typedef void (*JsonCallback)(const String& json);

  void begin(Stream& outputStream);
  void setJsonCallback(JsonCallback callback) { jsonCallback_ = callback; }
  void publishTelemetry(const CarTelemetry& carTelemetry);
  void publishCommandAck(const String& commandName, bool success,
                         const String& message);
  void publishEvent(const String& eventName, const String& message);
  void publishModeChangedByButton(DriveMode fromMode, DriveMode toMode);

 private:
  Stream* outputStream_ = nullptr;
  JsonCallback jsonCallback_ = nullptr;
  void sendJson(const JsonDocument& doc);
};

