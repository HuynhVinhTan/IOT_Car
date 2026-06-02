#pragma once

#include <Arduino.h>
#include "car_types.h"

class SafetyGuard {
 public:
  SafetyStatus update(const DistanceReadings& distanceReadings,
                      const CliffReadings& cliffReadings);
  bool shouldBlockForwardMotion() const;
  bool shouldBlockBackwardMotion() const;
  bool shouldEmergencyStopAuto() const;

 private:
  bool enabledDistanceSensorInvalid(bool enabled, bool valid) const;

  SafetyStatus latestSafetyStatus_;
  int consecutiveSensorFailures_ = 0;
};
