#pragma once

#include <Arduino.h>
#include "car_types.h"
#include "cliff_sensor.h"

class CliffSensorArray {
 public:
  CliffSensorArray();

  void begin();
  void update(unsigned long currentTimeMs);
  const CliffReadings& getReadings() const;

 private:
  void updateOneSensor(CliffSensor& sensor, float& groundDistanceCm,
                       bool& valid, bool& cliffDetected);

  CliffSensor frontLeftSensor_;
  CliffSensor frontRightSensor_;
  CliffSensor rearLeftSensor_;
  CliffSensor rearRightSensor_;
  CliffReadings latestReadings_;
  unsigned long lastUpdateMs_ = 0;
};
