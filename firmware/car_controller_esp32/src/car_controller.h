#pragma once

#include <WiFi.h>
#include <WebSocketsClient.h>

class CarController {
 public:
  void begin();
  void update();

 private:
  void setupWiFi();
  void setupWebsocket();
  void onWebsocketEvent(WStype_t type, uint8_t * payload, size_t length);
  void handleCommand(const ParsedCommand& parsedCommand);
  void handleSetModeCommand(DriveMode requestedMode);
  void handleRemoteDriveCommand(const ParsedCommand& parsedCommand,
                                unsigned long nowMs);
  void handleModeButtonShortPress();
  void handleModeButtonLongPress();
  void updateManualRemoteMode(unsigned long nowMs);
  void updateSensorsIfDue(unsigned long nowMs);
  void updateLocalDisplay(unsigned long nowMs);
  void publishTelemetryIfDue(unsigned long nowMs);
  void enterIdleMode(const String& reason);
  void enterManualRemoteMode(const String& reason);
  void enterStatusDisplayMode(const String& reason);
  void enterEmergencyStop(const String& reason);
  bool isRunningMode(DriveMode driveMode) const;
  bool requestedRemoteMotionMovesForward() const;
  bool requestedRemoteMotionMovesBackward() const;
  bool motorSpeedsMoveForward(const MotorSpeeds& motorSpeeds) const;
  bool motorSpeedsMoveBackward(const MotorSpeeds& motorSpeeds) const;
  CarTelemetry buildTelemetry(unsigned long nowMs) const;
  bool commandAllowedInEmergency(CommandType commandType) const;

  Engine engine_;
  DistanceSensorArray distanceSensorArray_;
  CliffSensorArray cliffSensorArray_;
  SpeedSensor speedSensor_;
  CameraModule camera_;
  LocalStatusButton localStatusButton_;
  BatteryMonitor batteryMonitor_;
  LcdDisplay lcdDisplay_;
  CommandParser commandParser_;
  TelemetryPublisher telemetryPublisher_;
  SafetyGuard safetyGuard_;
  WebSocketsClient webSocket_;

  DriveMode currentDriveMode_ = DriveMode::Idle;
  SafetyStatus latestSafetyStatus_;
  DistanceReadings latestDistanceReadings_;
  CliffReadings latestCliffReadings_;
  MotorSpeeds latestRemoteMotorSpeeds_;
  String emergencyStopReason_;
  String controlSource_ = "NONE";
  bool personDetectedByAi_ = false;
  bool remoteCommandTimedOut_ = false;
  bool remoteForwardBlockedByObstacle_ = false;
  bool remoteBackwardBlockedByObstacle_ = false;
  String currentNode_ = "UNKNOWN";
  String homeNode_ = "HOME";
  String targetNode_ = "";
  RobotPose currentPose_;
  unsigned long lastTelemetryMs_ = 0;
  unsigned long lastSensorReadMs_ = 0;
  unsigned long lastCommandMs_ = 0;
  unsigned long lastRemoteDriveCommandMs_ = 0;
};

