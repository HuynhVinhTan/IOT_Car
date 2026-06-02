#pragma once

#include <Arduino.h>

constexpr unsigned long SERIAL_BAUD_RATE = 115200;
constexpr unsigned long JOYSTICK_TELEMETRY_INTERVAL_MS = 50;
constexpr unsigned long JOYSTICK_BUTTON_DEBOUNCE_MS = 30;
constexpr size_t MAX_SERIAL_COMMAND_LENGTH = 192;

constexpr const char* JOYSTICK_BOARD_NAME = "ESP8266MOD";
constexpr const char* ESP8266_ANALOG_WARNING =
    "ADS1115 not connected. ESP8266 cannot read two joystick axes from A0.";

struct JoystickReading {
  unsigned long timestampMs = 0;
  bool ads1115Connected = false;
  int rawX = 0;
  int rawY = 0;
  float normalizedX = 0.0F;
  float normalizedY = 0.0F;
  bool deadzoneApplied = true;
  bool joystickButtonPressed = false;
  bool remoteModeButtonPressed = false;
  bool alertSirenActive = false;
  bool alertEnabled = true;
  const char* warning = nullptr;
};

enum class RouteButtonEventType {
  None,
  PreviousSegment,
  NextSegment,
  ConfirmSegment,
  AutoInferSegment,
  CancelSegment,
  HeadingHint
};

struct RouteButtonEvent {
  RouteButtonEventType type = RouteButtonEventType::None;
  unsigned long timestampMs = 0;
  float hintX = 0.0F;
  float hintY = 0.0F;
};
