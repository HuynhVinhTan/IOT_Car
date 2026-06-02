#include "cliff_sensor.h"

#include "pin_config.h"

CliffSensor::CliffSensor(int analogPin, bool enabled) {
  configure(analogPin, enabled);
}

void CliffSensor::configure(int analogPin, bool enabled) {
  analogPin_ = analogPin;
  enabled_ = enabled;
  lastReadValid_ = false;
}

void CliffSensor::begin() {
  if (!enabled_) {
    return;
  }

  pinMode(analogPin_, INPUT);
#if defined(ARDUINO_ARCH_ESP32)
  analogSetPinAttenuation(analogPin_, ADC_11db);
#endif
}

float CliffSensor::readGroundDistanceCm() {
  if (!enabled_) {
    lastReadValid_ = false;
    return 0.0F;
  }

  const int rawAdcValue = analogRead(analogPin_);
  lastReadValid_ = true;

  const float adcRange =
      static_cast<float>(CLIFF_SENSOR_NEAR_ADC_VALUE -
                         CLIFF_SENSOR_FAR_ADC_VALUE);
  if (adcRange <= 0.0F) {
    return NORMAL_GROUND_DISTANCE_CM;
  }

  float normalizedDistance =
      static_cast<float>(CLIFF_SENSOR_NEAR_ADC_VALUE - rawAdcValue) / adcRange;
  normalizedDistance = constrain(normalizedDistance, 0.0F, 1.0F);

  return CLIFF_SENSOR_MIN_DISTANCE_CM +
         normalizedDistance *
             (CLIFF_SENSOR_MAX_DISTANCE_CM - CLIFF_SENSOR_MIN_DISTANCE_CM);
}

bool CliffSensor::lastReadWasValid() const {
  return lastReadValid_;
}

bool CliffSensor::isEnabled() const {
  return enabled_;
}
