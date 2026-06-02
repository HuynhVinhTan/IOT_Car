#pragma once

#include <Arduino.h>
#include <LiquidCrystal_I2C.h>
#include "car_types.h"

class LcdDisplay {
 public:
  LcdDisplay();

  void begin();
  void turnOn();
  void turnOff();
  bool isEnabled() const;
  void updateStatus(DriveMode currentDriveMode, int batteryPercent,
                    float batteryVoltage, const char* currentNode,
                    bool obstacleDetected, bool cliffDetected,
                    bool personDetected, const char* emergencyReason,
                    unsigned long currentTimeMs);
  const char* status() const;

 private:
  void renderNormalStatus(DriveMode currentDriveMode, int batteryPercent,
                          float batteryVoltage, const char* currentNode,
                          bool obstacleDetected, bool cliffDetected);
  void renderEmergencyStatus(const char* emergencyReason, int batteryPercent);
  void renderAiAlert(int batteryPercent, const char* currentNode);
  void printPaddedLine(uint8_t row, const String& text);

  LiquidCrystal_I2C lcd_;
  unsigned long lastUpdateMs_ = 0;
  String latestLine1_;
  String latestLine2_;
  bool available_ = false;
  bool enabled_ = false;
};
