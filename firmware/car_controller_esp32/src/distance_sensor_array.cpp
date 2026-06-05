#include "distance_sensor_array.h"

#include "pin_config.h"

DistanceSensorArray::DistanceSensorArray()
    : frontSensor_(FRONT_ULTRASONIC_TRIG_PIN, FRONT_ULTRASONIC_ECHO_PIN,
                   ENABLE_FRONT_ULTRASONIC),
      leftSensor_(LEFT_ULTRASONIC_TRIG_PIN, LEFT_ULTRASONIC_ECHO_PIN,
                  ENABLE_LEFT_ULTRASONIC),
      rightSensor_(RIGHT_ULTRASONIC_TRIG_PIN, RIGHT_ULTRASONIC_ECHO_PIN,
                   ENABLE_RIGHT_ULTRASONIC),
      rearSensor_(0, 0, false) {
  latestReadings_.frontEnabled = ENABLE_FRONT_ULTRASONIC;
  latestReadings_.leftEnabled = ENABLE_LEFT_ULTRASONIC;
  latestReadings_.rightEnabled = ENABLE_RIGHT_ULTRASONIC;
  latestReadings_.rearEnabled = false;
}

void DistanceSensorArray::begin() {
  frontSensor_.begin();
  leftSensor_.begin();
  rightSensor_.begin();
}

void DistanceSensorArray::update(unsigned long currentTimeMs) {
  if (lastUpdateMs_ != 0 &&
      currentTimeMs - lastUpdateMs_ < SENSOR_READ_INTERVAL_MS) {
    return;
  }

  latestReadings_.frontEnabled = frontSensor_.isEnabled();
  latestReadings_.leftEnabled = leftSensor_.isEnabled();
  latestReadings_.rightEnabled = rightSensor_.isEnabled();
  latestReadings_.rearEnabled = rearSensor_.isEnabled();

  updateOneSensor(frontSensor_, SAFE_FRONT_DISTANCE_CM,
                  latestReadings_.frontDistanceCm,
                  latestReadings_.frontValid,
                  latestReadings_.obstacleFront);
  updateOneSensor(leftSensor_, SAFE_SIDE_DISTANCE_CM,
                  latestReadings_.leftDistanceCm,
                  latestReadings_.leftValid,
                  latestReadings_.obstacleLeft);
  updateOneSensor(rightSensor_, SAFE_SIDE_DISTANCE_CM,
                  latestReadings_.rightDistanceCm,
                  latestReadings_.rightValid,
                  latestReadings_.obstacleRight);
  updateOneSensor(rearSensor_, SAFE_REAR_DISTANCE_CM,
                  latestReadings_.rearDistanceCm,
                  latestReadings_.rearValid,
                  latestReadings_.obstacleRear);

  lastUpdateMs_ = currentTimeMs;
}

const DistanceReadings& DistanceSensorArray::getReadings() const {
  return latestReadings_;
}

void DistanceSensorArray::updateOneSensor(UltrasonicSensor& sensor,
                                          float safeDistanceCm,
                                          float& distanceCm, bool& valid,
                                          bool& obstacleDetected) {
  if (!sensor.isEnabled()) {
    distanceCm = 0.0F;
    valid = false;
    obstacleDetected = false;
    return;
  }

  distanceCm = sensor.readDistanceCm();
  valid = sensor.lastReadWasValid();
  obstacleDetected = valid && distanceCm > 0.0F && distanceCm < safeDistanceCm;
}
