#include "telemetry.h"

#include <ArduinoJson.h>
#include <math.h>

void TelemetryPublisher::begin(Stream& outputStream) {
  outputStream_ = &outputStream;
}

void TelemetryPublisher::sendJson(const JsonDocument& doc) {
  if (jsonCallback_) {
    String json;
    serializeJson(doc, json);
    jsonCallback_(json);
  }

  if (outputStream_) {
    serializeJson(doc, *outputStream_);
    outputStream_->println();
  }
}

void TelemetryPublisher::publishTelemetry(const CarTelemetry& carTelemetry) {
  JsonDocument telemetryDocument;
  telemetryDocument["type"] = "car_telemetry";
  telemetryDocument["timestamp_ms"] = carTelemetry.timestampMs;
  telemetryDocument["board"] = CAR_BOARD_NAME;
  telemetryDocument["mode"] = driveModeToString(carTelemetry.mode);
  telemetryDocument["battery_voltage"] = carTelemetry.batteryVoltage;
  telemetryDocument["battery_percent"] = carTelemetry.batteryPercent;
  telemetryDocument["left_motor_speed"] = carTelemetry.leftMotorSpeed;
  telemetryDocument["right_motor_speed"] = carTelemetry.rightMotorSpeed;
  telemetryDocument["left_speed_value"] = carTelemetry.leftSpeedValue;
  telemetryDocument["right_speed_value"] = carTelemetry.rightSpeedValue;
  telemetryDocument["desired_left_motor_speed"] = carTelemetry.desiredLeftMotorSpeed;
  telemetryDocument["desired_right_motor_speed"] = carTelemetry.desiredRightMotorSpeed;
  telemetryDocument["effective_left_motor_speed"] = carTelemetry.effectiveLeftMotorSpeed;
  telemetryDocument["effective_right_motor_speed"] = carTelemetry.effectiveRightMotorSpeed;
  telemetryDocument["safety_override_active"] = carTelemetry.forwardUnsafe || carTelemetry.backwardUnsafe;
  telemetryDocument["remote_command_timed_out"] = carTelemetry.remoteCommandTimedOut;

  if (carTelemetry.distanceValid) {
    telemetryDocument["distance_cm"] = carTelemetry.distanceCm;
  } else {
    telemetryDocument["distance_cm"] = nullptr;
  }

  telemetryDocument["obstacle_detected"] = carTelemetry.obstacleDetected;
  
  // Distances
  if (carTelemetry.distanceReadings.frontValid) telemetryDocument["front_distance_cm"] = carTelemetry.distanceReadings.frontDistanceCm;
  else telemetryDocument["front_distance_cm"] = nullptr;
  
  if (carTelemetry.distanceReadings.leftValid) telemetryDocument["left_distance_cm"] = carTelemetry.distanceReadings.leftDistanceCm;
  else telemetryDocument["left_distance_cm"] = nullptr;
  
  if (carTelemetry.distanceReadings.rightValid) telemetryDocument["right_distance_cm"] = carTelemetry.distanceReadings.rightDistanceCm;
  else telemetryDocument["right_distance_cm"] = nullptr;
  
  if (carTelemetry.distanceReadings.rearValid) telemetryDocument["rear_distance_cm"] = carTelemetry.distanceReadings.rearDistanceCm;
  else telemetryDocument["rear_distance_cm"] = nullptr;

  telemetryDocument["obstacle_front"] = carTelemetry.distanceReadings.obstacleFront;
  telemetryDocument["obstacle_left"] = carTelemetry.distanceReadings.obstacleLeft;
  telemetryDocument["obstacle_right"] = carTelemetry.distanceReadings.obstacleRight;
  telemetryDocument["obstacle_rear"] = carTelemetry.distanceReadings.obstacleRear;
  
  // Cliffs
  if (carTelemetry.cliffReadings.frontLeftValid) telemetryDocument["front_left_ground_cm"] = carTelemetry.cliffReadings.frontLeftGroundDistanceCm;
  else telemetryDocument["front_left_ground_cm"] = nullptr;
  
  if (carTelemetry.cliffReadings.frontRightValid) telemetryDocument["front_right_ground_cm"] = carTelemetry.cliffReadings.frontRightGroundDistanceCm;
  else telemetryDocument["front_right_ground_cm"] = nullptr;
  
  if (carTelemetry.cliffReadings.rearLeftValid) telemetryDocument["rear_left_ground_cm"] = carTelemetry.cliffReadings.rearLeftGroundDistanceCm;
  else telemetryDocument["rear_left_ground_cm"] = nullptr;
  
  if (carTelemetry.cliffReadings.rearRightValid) telemetryDocument["rear_right_ground_cm"] = carTelemetry.cliffReadings.rearRightGroundDistanceCm;
  else telemetryDocument["rear_right_ground_cm"] = nullptr;

  telemetryDocument["front_cliff_detected"] = carTelemetry.cliffReadings.frontCliffDetected;
  telemetryDocument["rear_cliff_detected"] = carTelemetry.cliffReadings.rearCliffDetected;
  telemetryDocument["cliff_detected"] = carTelemetry.cliffDetected;
  telemetryDocument["forward_unsafe"] = carTelemetry.forwardUnsafe;
  telemetryDocument["backward_unsafe"] = carTelemetry.backwardUnsafe;
  telemetryDocument["person_detected"] = carTelemetry.personDetected;
  telemetryDocument["emergency_reason"] = carTelemetry.emergencyStopReason;
  telemetryDocument["control_source"] = carTelemetry.controlSource;
  telemetryDocument["lcd_status"] = carTelemetry.lcdStatus;
  telemetryDocument["lcd_enabled"] = carTelemetry.lcdEnabled;
  telemetryDocument["current_node"] = carTelemetry.currentNode;
  telemetryDocument["home_node"] = carTelemetry.homeNode;
  telemetryDocument["target_node"] = carTelemetry.targetNode;

  if (carTelemetry.currentPose.valid) {
    JsonObject poseDocument = telemetryDocument["current_pose"].to<JsonObject>();
    poseDocument["x"] = carTelemetry.currentPose.x;
    poseDocument["y"] = carTelemetry.currentPose.y;
    poseDocument["heading_deg"] = carTelemetry.currentPose.headingDeg;
  } else {
    telemetryDocument["current_pose"] = nullptr;
  }

  sendJson(telemetryDocument);
}

void TelemetryPublisher::publishCommandAck(const String& commandName,
                                           bool success,
                                           const String& message) {
  JsonDocument ackDocument;
  ackDocument["type"] = "command_ack";
  ackDocument["command"] = commandName;
  ackDocument["success"] = success;
  ackDocument["message"] = message;

  sendJson(ackDocument);
}

void TelemetryPublisher::publishEvent(const String& eventName,
                                      const String& message) {
  JsonDocument eventDocument;
  eventDocument["type"] = "car_event";
  eventDocument["event"] = eventName;
  eventDocument["message"] = message;
  eventDocument["timestamp_ms"] = millis();

  sendJson(eventDocument);
}

void TelemetryPublisher::publishModeChangedByButton(DriveMode fromMode,
                                                    DriveMode toMode) {
  JsonDocument eventDocument;
  eventDocument["type"] = "car_event";
  eventDocument["event"] = "mode_changed_by_button";
  eventDocument["from_mode"] = driveModeToString(fromMode);
  eventDocument["to_mode"] = driveModeToString(toMode);
  eventDocument["timestamp_ms"] = millis();

  sendJson(eventDocument);
}

