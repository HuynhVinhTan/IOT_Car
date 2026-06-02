#pragma once

#include <Arduino.h>

constexpr unsigned long SERIAL_BAUD_RATE = 115200;
constexpr unsigned long TELEMETRY_INTERVAL_MS = 200;
constexpr unsigned long SENSOR_READ_INTERVAL_MS = 100;
constexpr unsigned long PATH_RECORD_INTERVAL_MS = 100;
constexpr unsigned long SPEED_SAMPLE_INTERVAL_MS = 500;
constexpr unsigned long COMMAND_TIMEOUT_MS = 1000;

constexpr float SAFE_DISTANCE_CM = 20.0F;
constexpr float SAFE_FRONT_DISTANCE_CM = 25.0F;
constexpr float SAFE_SIDE_DISTANCE_CM = 15.0F;
constexpr float SAFE_REAR_DISTANCE_CM = 20.0F;
constexpr unsigned long ULTRASONIC_TIMEOUT_US = 25000;

constexpr int MAX_MOTOR_SPEED = 255;
constexpr int MIN_MOTOR_SPEED = -255;
constexpr int MAX_RECORDED_PATH_POINTS = 500;


constexpr int MOTOR_PWM_FREQUENCY_HZ = 20000;
constexpr int MOTOR_PWM_RESOLUTION_BITS = 8;
constexpr int LEFT_MOTOR_PWM_CHANNEL = 14;
constexpr int RIGHT_MOTOR_PWM_CHANNEL = 15;
constexpr bool LEFT_MOTOR_FORWARD_LEVEL = HIGH;
constexpr bool RIGHT_MOTOR_FORWARD_LEVEL = HIGH;

constexpr size_t MAX_SERIAL_COMMAND_LENGTH = 256;
constexpr int MAX_ULTRASONIC_FAILURES = 5;
constexpr bool STOP_ON_PERSON_DETECTED = false;
constexpr const char* CAR_BOARD_NAME = "ESP32_WROOM";

enum class DriveMode {
  Idle,
  ManualRemote,
  LearningMap,
  AutoSearch,
  ReturnHome,
  StatusDisplay,
  EmergencyStop
};

inline const char* driveModeToString(DriveMode mode) {
  switch (mode) {
    case DriveMode::Idle:
      return "IDLE";
    case DriveMode::ManualRemote:
      return "MANUAL_REMOTE";
    case DriveMode::LearningMap:
      return "LEARNING_MAP";
    case DriveMode::AutoSearch:
      return "AUTO_SEARCH";
    case DriveMode::ReturnHome:
      return "RETURN_HOME";
    case DriveMode::StatusDisplay:
      return "STATUS_DISPLAY";
    case DriveMode::EmergencyStop:
      return "EMERGENCY_STOP";
    default:
      return "UNKNOWN";
  }
}

inline bool parseDriveMode(const char* modeText, DriveMode& parsedMode) {
  if (modeText == nullptr) {
    return false;
  }

  if (strcmp(modeText, "IDLE") == 0) {
    parsedMode = DriveMode::Idle;
    return true;
  }

  if (strcmp(modeText, "MANUAL_REMOTE") == 0) {
    parsedMode = DriveMode::ManualRemote;
    return true;
  }

  if (strcmp(modeText, "LEARNING_MAP") == 0) {
    parsedMode = DriveMode::LearningMap;
    return true;
  }

  if (strcmp(modeText, "AUTO_SEARCH") == 0 ||
      strcmp(modeText, "AUTO") == 0 ||
      strcmp(modeText, "AUTO_REPLAY") == 0) {
    parsedMode = DriveMode::AutoSearch;
    return true;
  }

  if (strcmp(modeText, "RETURN_HOME") == 0) {
    parsedMode = DriveMode::ReturnHome;
    return true;
  }

  if (strcmp(modeText, "STATUS_DISPLAY") == 0 ||
      strcmp(modeText, "IDLE_STATUS") == 0) {
    parsedMode = DriveMode::StatusDisplay;
    return true;
  }

  if (strcmp(modeText, "EMERGENCY_STOP") == 0) {
    parsedMode = DriveMode::EmergencyStop;
    return true;
  }

  return false;
}

struct MotorSpeeds {
  int leftMotorSpeed = 0;
  int rightMotorSpeed = 0;
};

struct RobotPose {
  float x = 0.0F;
  float y = 0.0F;
  float headingDeg = 0.0F;
  bool valid = false;
};

struct DistanceReadings {
  float frontDistanceCm = 0.0F;
  float leftDistanceCm = 0.0F;
  float rightDistanceCm = 0.0F;
  float rearDistanceCm = 0.0F;

  bool frontEnabled = false;
  bool leftEnabled = false;
  bool rightEnabled = false;
  bool rearEnabled = false;

  bool frontValid = false;
  bool leftValid = false;
  bool rightValid = false;
  bool rearValid = false;

  bool obstacleFront = false;
  bool obstacleLeft = false;
  bool obstacleRight = false;
  bool obstacleRear = false;
};

struct CliffReadings {
  float frontLeftGroundDistanceCm = 0.0F;
  float frontRightGroundDistanceCm = 0.0F;
  float rearLeftGroundDistanceCm = 0.0F;
  float rearRightGroundDistanceCm = 0.0F;

  bool frontLeftEnabled = false;
  bool frontRightEnabled = false;
  bool rearLeftEnabled = false;
  bool rearRightEnabled = false;

  bool frontLeftValid = false;
  bool frontRightValid = false;
  bool rearLeftValid = false;
  bool rearRightValid = false;

  bool frontLeftCliffDetected = false;
  bool frontRightCliffDetected = false;
  bool rearLeftCliffDetected = false;
  bool rearRightCliffDetected = false;

  bool frontCliffDetected = false;
  bool rearCliffDetected = false;
  bool cliffDetected = false;
  bool forwardUnsafe = false;
  bool backwardUnsafe = false;
};

struct PathPoint {
  unsigned long timestampMs = 0;
  int leftMotorSpeed = 0;
  int rightMotorSpeed = 0;
  float distanceCm = 0.0F;
  float speedValue = 0.0F;
  bool obstacleDetected = false;
};

struct SafetyStatus {
  bool obstacleDetected = false;
  bool obstacleFront = false;
  bool obstacleLeft = false;
  bool obstacleRight = false;
  bool obstacleRear = false;
  bool cliffDetected = false;
  bool forwardUnsafe = false;
  bool backwardUnsafe = false;
  bool sensorFault = false;
};

struct CarTelemetry {
  DriveMode mode = DriveMode::Idle;
  unsigned long timestampMs = 0;
  int leftMotorSpeed = 0;
  int rightMotorSpeed = 0;
  float speedValue = 0.0F;
  float distanceCm = 0.0F;
  bool distanceValid = false;
  DistanceReadings distanceReadings;
  CliffReadings cliffReadings;
  bool obstacleDetected = false;
  bool forwardUnsafe = false;
  bool backwardUnsafe = false;
  bool cliffDetected = false;
  bool isRecording = false;
  size_t recordedPathPoints = 0;
  bool isAutoRunning = false;
  bool personDetected = false;
  String emergencyStopReason;
  String controlSource = "NONE";
  float batteryVoltage = 0.0F;
  int batteryPercent = 0;
  String lcdStatus = "OK";
  bool lcdEnabled = false;
  String currentNode = "UNKNOWN";
  String homeNode = "HOME";
  String targetNode = "";
  RobotPose currentPose;
};
