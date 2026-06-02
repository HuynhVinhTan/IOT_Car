#include "joystick_reader.h"

#include <math.h>
#include <Wire.h>
#include "pin_config.h"

bool JoystickReader::begin() {
  Wire.begin(ADS1115_SDA_PIN, ADS1115_SCL_PIN);
  latestReading_.ads1115Connected = ads1115_.begin(ADS1115_I2C_ADDRESS);
  if (latestReading_.ads1115Connected) {
    ads1115_.setGain(GAIN_ONE);
    latestReading_.warning = nullptr;
  } else {
    latestReading_.warning = ESP8266_ANALOG_WARNING;
  }

  pinMode(JOYSTICK_BUTTON_PIN, INPUT_PULLUP);

  stableButtonPressed_ = digitalRead(JOYSTICK_BUTTON_PIN) == LOW;
  lastRawButtonPressed_ = stableButtonPressed_;
  lastButtonDebounceMs_ = millis();
  return latestReading_.ads1115Connected;
}

void JoystickReader::update(unsigned long currentTimeMs) {
  updateButton(currentTimeMs);

  latestReading_.timestampMs = currentTimeMs;
  latestReading_.joystickButtonPressed = stableButtonPressed_;

  if (!latestReading_.ads1115Connected) {
    latestReading_.rawX = 0;
    latestReading_.rawY = 0;
    latestReading_.normalizedX = 0.0F;
    latestReading_.normalizedY = 0.0F;
    latestReading_.deadzoneApplied = true;
    latestReading_.warning = ESP8266_ANALOG_WARNING;
    return;
  }

  latestReading_.rawX = ads1115_.readADC_SingleEnded(ADS1115_JOYSTICK_X_CHANNEL);
  latestReading_.rawY = ads1115_.readADC_SingleEnded(ADS1115_JOYSTICK_Y_CHANNEL);
  latestReading_.normalizedX =
      applyDeadzone(normalizeAxis(latestReading_.rawX, JOYSTICK_X_CENTER_RAW,
                                  JOYSTICK_X_MIN_RAW, JOYSTICK_X_MAX_RAW));
  latestReading_.normalizedY =
      applyDeadzone(normalizeAxis(latestReading_.rawY, JOYSTICK_Y_CENTER_RAW,
                                  JOYSTICK_Y_MIN_RAW, JOYSTICK_Y_MAX_RAW));
  latestReading_.deadzoneApplied =
      latestReading_.normalizedX == 0.0F && latestReading_.normalizedY == 0.0F;
  latestReading_.warning = nullptr;
}

const JoystickReading& JoystickReader::getState() const {
  return latestReading_;
}

float JoystickReader::normalizeAxis(int rawValue, int centerValue, int minValue,
                                    int maxValue) const {
  if (rawValue >= centerValue) {
    const int positiveRange = max(maxValue - centerValue, 1);
    return constrain(static_cast<float>(rawValue - centerValue) /
                         static_cast<float>(positiveRange),
                     -1.0F, 1.0F);
  }

  const int negativeRange = max(centerValue - minValue, 1);
  return constrain(static_cast<float>(rawValue - centerValue) /
                       static_cast<float>(negativeRange),
                   -1.0F, 1.0F);
}

float JoystickReader::applyDeadzone(float normalizedValue) const {
  if (fabs(normalizedValue) < JOYSTICK_DEADZONE) {
    return 0.0F;
  }

  return normalizedValue;
}

void JoystickReader::updateButton(unsigned long currentTimeMs) {
  const bool rawButtonPressed = digitalRead(JOYSTICK_BUTTON_PIN) == LOW;

  if (rawButtonPressed != lastRawButtonPressed_) {
    lastButtonDebounceMs_ = currentTimeMs;
    lastRawButtonPressed_ = rawButtonPressed;
  }

  if (currentTimeMs - lastButtonDebounceMs_ < JOYSTICK_BUTTON_DEBOUNCE_MS) {
    return;
  }

  stableButtonPressed_ = rawButtonPressed;
}
