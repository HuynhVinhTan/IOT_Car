#pragma once

#include <Arduino.h>

class BatteryMonitor {
 public:
  void begin();
  void update(unsigned long currentTimeMs);
  float getBatteryVoltage() const;
  int getBatteryPercent() const;

 private:
  int calculateBatteryPercent(float batteryVoltage) const;

  unsigned long lastReadMs_ = 0;
  float latestBatteryVoltage_ = 0.0F;
  int latestBatteryPercent_ = 0;
};
