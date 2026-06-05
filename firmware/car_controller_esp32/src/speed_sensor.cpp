#include "speed_sensor.h"

#include "pin_config.h"

SpeedSensor::SpeedSensor(int sensorPin) : sensorPin_(sensorPin) {}

void SpeedSensor::begin() {
  pinMode(sensorPin_, INPUT_PULLUP);
  attachInterruptArg(digitalPinToInterrupt(sensorPin_), handlePulseInterrupt, this,
                     RISING);
  lastSampleMs_ = millis();
}

void SpeedSensor::update(unsigned long nowMs) {
  if (nowMs - lastSampleMs_ < SPEED_SAMPLE_INTERVAL_MS) {
    return;
  }

  noInterrupts();
  const unsigned long currentPulseCount = pulseCount_;
  interrupts();

  const unsigned long elapsedMs = nowMs - lastSampleMs_;
  const unsigned long pulsesSinceLastSample =
      currentPulseCount - lastPulseCount_;

  latestSpeedValue_ =
      (static_cast<float>(pulsesSinceLastSample) * 1000.0F) /
      static_cast<float>(elapsedMs);

  lastPulseCount_ = currentPulseCount;
  lastSampleMs_ = nowMs;
}

float SpeedSensor::speedValue() const {
  return latestSpeedValue_;
}

void IRAM_ATTR SpeedSensor::handlePulseInterrupt(void* arg) {
  SpeedSensor* instance = static_cast<SpeedSensor*>(arg);
  if (instance != nullptr) {
    instance->pulseCount_++;
  }
}
