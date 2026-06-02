#pragma once

#include <Arduino.h>

class CliffSensor {
 public:
  CliffSensor() = default;
  CliffSensor(int analogPin, bool enabled);

  void configure(int analogPin, bool enabled);
  void begin();
  float readGroundDistanceCm();
  bool lastReadWasValid() const;
  bool isEnabled() const;

 private:
  int analogPin_ = -1;
  bool enabled_ = false;
  bool lastReadValid_ = false;
};
