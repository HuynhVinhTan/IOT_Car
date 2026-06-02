#pragma once

#include <Arduino.h>
#include "car_types.h"
#include "ultrasonic_sensor.h"

class DistanceSensorArray {
 public:
  DistanceSensorArray();

  void begin();
  void update(unsigned long currentTimeMs);
  const DistanceReadings& getReadings() const;

 private:
  void updateOneSensor(UltrasonicSensor& sensor, float safeDistanceCm,
                       float& distanceCm, bool& valid,
                       bool& obstacleDetected);

  UltrasonicSensor frontSensor_;
  UltrasonicSensor leftSensor_;
  UltrasonicSensor rightSensor_;
  UltrasonicSensor rearSensor_;
  DistanceReadings latestReadings_;
  unsigned long lastUpdateMs_ = 0;
};
