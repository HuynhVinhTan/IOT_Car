#include "telemetry.h"

#include <ArduinoJson.h>

void JoystickTelemetryPublisher::begin(Stream& outputStream) {
  outputStream_ = &outputStream;
}

void JoystickTelemetryPublisher::publish(
    const JoystickReading& joystickReading) {
  if (outputStream_ == nullptr) {
    return;
  }

  JsonDocument telemetryDocument;
  telemetryDocument["type"] = "joystick_telemetry";
  telemetryDocument["timestamp_ms"] = joystickReading.timestampMs;
  telemetryDocument["board"] = JOYSTICK_BOARD_NAME;
  telemetryDocument["ads1115_connected"] = joystickReading.ads1115Connected;
  telemetryDocument["raw_x"] = joystickReading.rawX;
  telemetryDocument["raw_y"] = joystickReading.rawY;
  telemetryDocument["normalized_x"] = joystickReading.normalizedX;
  telemetryDocument["normalized_y"] = joystickReading.normalizedY;
  telemetryDocument["deadzone_applied"] = joystickReading.deadzoneApplied;
  telemetryDocument["button_pressed"] = joystickReading.joystickButtonPressed;
  telemetryDocument["joystick_button_pressed"] =
      joystickReading.joystickButtonPressed;
  telemetryDocument["remote_mode_button_pressed"] =
      joystickReading.remoteModeButtonPressed;
  telemetryDocument["alert_siren_active"] = joystickReading.alertSirenActive;
  telemetryDocument["alert_enabled"] = joystickReading.alertEnabled;
  if (joystickReading.warning != nullptr) {
    telemetryDocument["warning"] = joystickReading.warning;
  } else {
    telemetryDocument["warning"] = nullptr;
  }

  serializeJson(telemetryDocument, *outputStream_);
  outputStream_->println();
}

void JoystickTelemetryPublisher::publishCommandAck(const String& commandName,
                                                   bool success,
                                                   const String& message) {
  if (outputStream_ == nullptr) {
    return;
  }

  JsonDocument ackDocument;
  ackDocument["type"] = "joystick_command_ack";
  ackDocument["command"] = commandName;
  ackDocument["success"] = success;
  ackDocument["message"] = message;

  serializeJson(ackDocument, *outputStream_);
  outputStream_->println();
}

void JoystickTelemetryPublisher::publishRemoteButtonEvent(
    const String& eventName, unsigned long timestampMs) {
  if (outputStream_ == nullptr) {
    return;
  }

  JsonDocument eventDocument;
  eventDocument["type"] = "remote_button_event";
  eventDocument["event"] = eventName;
  eventDocument["timestamp_ms"] = timestampMs;

  serializeJson(eventDocument, *outputStream_);
  outputStream_->println();
}

void JoystickTelemetryPublisher::publishRemoteRouteEvent(
    const RouteButtonEvent& event) {
  if (!outputStream_) {
    return;
  }
  JsonDocument doc;
  doc["type"] = "remote_route_event";
  doc["timestamp_ms"] = event.timestampMs;

  switch (event.type) {
    case RouteButtonEventType::PreviousSegment:
      doc["event"] = "previous_segment";
      break;
    case RouteButtonEventType::NextSegment:
      doc["event"] = "next_segment";
      break;
    case RouteButtonEventType::ConfirmSegment:
      doc["event"] = "segment_selected";
      break;
    case RouteButtonEventType::AutoInferSegment:
      doc["event"] = "auto_infer_segment_requested";
      break;
    case RouteButtonEventType::CancelSegment:
      doc["event"] = "segment_command_cancelled";
      break;
    case RouteButtonEventType::HeadingHint:
      doc["event"] = "segment_heading_hint";
      doc["heading_hint_x"] = event.hintX;
      doc["heading_hint_y"] = event.hintY;
      break;
    default:
      return;
  }

  serializeJson(doc, *outputStream_);
  outputStream_->println();
}
