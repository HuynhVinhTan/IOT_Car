#include "ultrasonic_sensor.h"

#include "pin_config.h"

UltrasonicSensor::UltrasonicSensor(int trigPin, int echoPin, bool enabled) {
  configure(trigPin, echoPin, enabled);
}

void UltrasonicSensor::configure(int trigPin, int echoPin, bool enabled) {
  trigPin_ = trigPin;
  echoPin_ = echoPin;
  enabled_ = enabled;
  lastReadValid_ = false;
}

void UltrasonicSensor::begin() {
  if (!enabled_) {
    return;
  }

  pinMode(trigPin_, OUTPUT);
  pinMode(echoPin_, INPUT);
  digitalWrite(trigPin_, LOW);
}

float UltrasonicSensor::readDistanceCm() {
  if (!enabled_) {
    lastReadValid_ = false;
    return 0.0F;
  }

  digitalWrite(trigPin_, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin_, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin_, LOW);

  const unsigned long echoDurationUs =
      pulseIn(echoPin_, HIGH, ULTRASONIC_TIMEOUT_US);

  if (echoDurationUs == 0) {
    lastReadValid_ = false;
    return 0.0F;
  }

  lastReadValid_ = true;
  return static_cast<float>(echoDurationUs) * 0.0343F / 2.0F;
}

bool UltrasonicSensor::lastReadWasValid() const {
  return lastReadValid_;
}

bool UltrasonicSensor::isEnabled() const {
  return enabled_;
}
