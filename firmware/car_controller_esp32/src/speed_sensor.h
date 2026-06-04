#pragma once

#include <Arduino.h>
#include "car_types.h"

class SpeedSensor {
 public:
  SpeedSensor(int sensorPin);
  void begin();
  void update(unsigned long nowMs);
  float speedValue() const;

 private:
  static void IRAM_ATTR handlePulseInterrupt();

  int sensorPin_;
  volatile unsigned long pulseCount_ = 0;
  unsigned long lastSampleMs_ = 0;
  unsigned long lastPulseCount_ = 0;
  float latestSpeedValue_ = 0.0F;

  static SpeedSensor* activeInstance_;
};
