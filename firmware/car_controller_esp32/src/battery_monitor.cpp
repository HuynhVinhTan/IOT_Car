#include "battery_monitor.h"

#include "pin_config.h"

void BatteryMonitor::begin() {
  pinMode(BATTERY_ADC_PIN, INPUT);
  analogReadResolution(12);
  analogSetPinAttenuation(BATTERY_ADC_PIN, ADC_11db);
  update(millis());
}

void BatteryMonitor::update(unsigned long currentTimeMs) {
  if (lastReadMs_ != 0 &&
      currentTimeMs - lastReadMs_ < BATTERY_READ_INTERVAL_MS) {
    return;
  }

  const int rawAdcValue = analogRead(BATTERY_ADC_PIN);
  const float adcVoltage =
      (static_cast<float>(rawAdcValue) / static_cast<float>(ADC_MAX_VALUE)) *
      ADC_REFERENCE_VOLTAGE;

  latestBatteryVoltage_ = adcVoltage * BATTERY_VOLTAGE_DIVIDER_RATIO;
  latestBatteryPercent_ = calculateBatteryPercent(latestBatteryVoltage_);
  lastReadMs_ = currentTimeMs;
}

float BatteryMonitor::getBatteryVoltage() const {
  return latestBatteryVoltage_;
}

int BatteryMonitor::getBatteryPercent() const {
  return latestBatteryPercent_;
}

int BatteryMonitor::calculateBatteryPercent(float batteryVoltage) const {
  const float batteryRange = BATTERY_MAX_VOLTAGE - BATTERY_MIN_VOLTAGE;
  if (batteryRange <= 0.0F) {
    return 0;
  }

  const float normalizedBatteryLevel =
      (batteryVoltage - BATTERY_MIN_VOLTAGE) / batteryRange;
  return constrain(static_cast<int>(normalizedBatteryLevel * 100.0F), 0, 100);
}
