#pragma once

#include <Arduino.h>
#include "car_types.h"

class UltrasonicSensor {
 public:
  UltrasonicSensor() = default;
  UltrasonicSensor(int trigPin, int echoPin, bool enabled);
  void configure(int trigPin, int echoPin, bool enabled);
  void begin();
  float readDistanceCm();
  bool lastReadWasValid() const;
  bool isEnabled() const;

 private:
  int trigPin_ = -1;
  int echoPin_ = -1;
  bool enabled_ = false;
  bool lastReadValid_ = false;
};
