#include "safety_guard.h"

SafetyStatus SafetyGuard::update(const DistanceReadings& distanceReadings,
                                 const CliffReadings& cliffReadings) {
  const bool anyEnabledSensorInvalid =
      enabledDistanceSensorInvalid(distanceReadings.frontEnabled,
                                   distanceReadings.frontValid) ||
      enabledDistanceSensorInvalid(distanceReadings.leftEnabled,
                                   distanceReadings.leftValid) ||
      enabledDistanceSensorInvalid(distanceReadings.rightEnabled,
                                   distanceReadings.rightValid) ||
      enabledDistanceSensorInvalid(distanceReadings.rearEnabled,
                                   distanceReadings.rearValid);

  if (anyEnabledSensorInvalid) {
    consecutiveSensorFailures_++;
  } else {
    consecutiveSensorFailures_ = 0;
  }

  latestSafetyStatus_.obstacleFront = distanceReadings.obstacleFront;
  latestSafetyStatus_.obstacleLeft = distanceReadings.obstacleLeft;
  latestSafetyStatus_.obstacleRight = distanceReadings.obstacleRight;
  latestSafetyStatus_.obstacleRear = distanceReadings.obstacleRear;
  latestSafetyStatus_.obstacleDetected =
      distanceReadings.obstacleFront || distanceReadings.obstacleLeft ||
      distanceReadings.obstacleRight || distanceReadings.obstacleRear;
  latestSafetyStatus_.cliffDetected = cliffReadings.cliffDetected;
  latestSafetyStatus_.forwardUnsafe =
      latestSafetyStatus_.obstacleFront || cliffReadings.forwardUnsafe;
  latestSafetyStatus_.backwardUnsafe =
      latestSafetyStatus_.obstacleRear || cliffReadings.backwardUnsafe;
  latestSafetyStatus_.sensorFault =
      consecutiveSensorFailures_ >= MAX_ULTRASONIC_FAILURES;

  return latestSafetyStatus_;
}

bool SafetyGuard::shouldBlockForwardMotion() const {
  return latestSafetyStatus_.forwardUnsafe;
}

bool SafetyGuard::shouldBlockBackwardMotion() const {
  return latestSafetyStatus_.backwardUnsafe;
}

bool SafetyGuard::shouldEmergencyStopAuto() const {
  return latestSafetyStatus_.cliffDetected || latestSafetyStatus_.sensorFault;
}

bool SafetyGuard::enabledDistanceSensorInvalid(bool enabled, bool valid) const {
  return enabled && !valid;
}
