#include "cliff_sensor_array.h"

#include "pin_config.h"

CliffSensorArray::CliffSensorArray()
    : frontLeftSensor_(FRONT_LEFT_CLIFF_SENSOR_PIN,
                       ENABLE_FRONT_LEFT_CLIFF_SENSOR),
      frontRightSensor_(FRONT_RIGHT_CLIFF_SENSOR_PIN,
                        ENABLE_FRONT_RIGHT_CLIFF_SENSOR),
      rearLeftSensor_(REAR_LEFT_CLIFF_SENSOR_PIN,
                      ENABLE_REAR_LEFT_CLIFF_SENSOR),
      rearRightSensor_(REAR_RIGHT_CLIFF_SENSOR_PIN,
                       ENABLE_REAR_RIGHT_CLIFF_SENSOR) {
  latestReadings_.frontLeftEnabled = ENABLE_FRONT_LEFT_CLIFF_SENSOR;
  latestReadings_.frontRightEnabled = ENABLE_FRONT_RIGHT_CLIFF_SENSOR;
  latestReadings_.rearLeftEnabled = ENABLE_REAR_LEFT_CLIFF_SENSOR;
  latestReadings_.rearRightEnabled = ENABLE_REAR_RIGHT_CLIFF_SENSOR;
}

void CliffSensorArray::begin() {
  frontLeftSensor_.begin();
  frontRightSensor_.begin();
  rearLeftSensor_.begin();
  rearRightSensor_.begin();
}

void CliffSensorArray::update(unsigned long currentTimeMs) {
  if (lastUpdateMs_ != 0 &&
      currentTimeMs - lastUpdateMs_ < SENSOR_READ_INTERVAL_MS) {
    return;
  }

  latestReadings_.frontLeftEnabled = frontLeftSensor_.isEnabled();
  latestReadings_.frontRightEnabled = frontRightSensor_.isEnabled();
  latestReadings_.rearLeftEnabled = rearLeftSensor_.isEnabled();
  latestReadings_.rearRightEnabled = rearRightSensor_.isEnabled();

  updateOneSensor(frontLeftSensor_,
                  latestReadings_.frontLeftGroundDistanceCm,
                  latestReadings_.frontLeftValid,
                  latestReadings_.frontLeftCliffDetected);
  updateOneSensor(frontRightSensor_,
                  latestReadings_.frontRightGroundDistanceCm,
                  latestReadings_.frontRightValid,
                  latestReadings_.frontRightCliffDetected);
  updateOneSensor(rearLeftSensor_, latestReadings_.rearLeftGroundDistanceCm,
                  latestReadings_.rearLeftValid,
                  latestReadings_.rearLeftCliffDetected);
  updateOneSensor(rearRightSensor_, latestReadings_.rearRightGroundDistanceCm,
                  latestReadings_.rearRightValid,
                  latestReadings_.rearRightCliffDetected);

  latestReadings_.frontCliffDetected =
      latestReadings_.frontLeftCliffDetected ||
      latestReadings_.frontRightCliffDetected;
  latestReadings_.rearCliffDetected =
      latestReadings_.rearLeftCliffDetected ||
      latestReadings_.rearRightCliffDetected;
  latestReadings_.cliffDetected = latestReadings_.frontCliffDetected ||
                                  latestReadings_.rearCliffDetected;
  latestReadings_.forwardUnsafe = latestReadings_.frontCliffDetected;
  latestReadings_.backwardUnsafe = latestReadings_.rearCliffDetected;

  lastUpdateMs_ = currentTimeMs;
}

const CliffReadings& CliffSensorArray::getReadings() const {
  return latestReadings_;
}

void CliffSensorArray::updateOneSensor(CliffSensor& sensor,
                                       float& groundDistanceCm, bool& valid,
                                       bool& cliffDetected) {
  if (!sensor.isEnabled()) {
    groundDistanceCm = 0.0F;
    valid = false;
    cliffDetected = false;
    return;
  }

  groundDistanceCm = sensor.readGroundDistanceCm();
  valid = sensor.lastReadWasValid();
  cliffDetected = valid && groundDistanceCm > CLIFF_DISTANCE_THRESHOLD_CM;
}
