#pragma once

#include <Arduino.h>
#include <Adafruit_ADS1X15.h>
#include "joystick_types.h"

class JoystickReader {
 public:
  bool begin();
  void update(unsigned long currentTimeMs);
  const JoystickReading& getState() const;

 private:
  float normalizeAxis(int rawValue, int centerValue, int minValue,
                      int maxValue) const;
  float applyDeadzone(float normalizedValue) const;
  void updateButton(unsigned long currentTimeMs);

  Adafruit_ADS1115 ads1115_;
  JoystickReading latestReading_;
  bool stableButtonPressed_ = false;
  bool lastRawButtonPressed_ = false;
  unsigned long lastButtonDebounceMs_ = 0;
};
