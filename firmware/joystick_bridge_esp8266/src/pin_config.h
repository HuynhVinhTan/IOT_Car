#pragma once

// ESP8266MOD has only one analog input. The two-axis joystick is read via
// ADS1115 over I2C: NodeMCU D1/GPIO5 = SCL, D2/GPIO4 = SDA.
constexpr int ADS1115_SCL_PIN = 5;
constexpr int ADS1115_SDA_PIN = 4;
constexpr uint8_t ADS1115_I2C_ADDRESS = 0x48;
constexpr int ADS1115_JOYSTICK_X_CHANNEL = 0;
constexpr int ADS1115_JOYSTICK_Y_CHANNEL = 1;

constexpr uint8_t PCF8574_I2C_ADDRESS = 0x20;
constexpr uint8_t PCF_PIN_ROUTE_PREV = 0;
constexpr uint8_t PCF_PIN_ROUTE_NEXT = 1;
constexpr uint8_t PCF_PIN_ROUTE_CONFIRM = 2;
constexpr unsigned long ROUTE_BUTTON_DEBOUNCE_MS = 50;
constexpr unsigned long ROUTE_BUTTON_LONG_PRESS_MS = 2000;

// TODO: calibrate these values with the real joystick and ADS1115 gain.
constexpr int JOYSTICK_X_MIN_RAW = 0;
constexpr int JOYSTICK_X_CENTER_RAW = 13200;
constexpr int JOYSTICK_X_MAX_RAW = 26400;
constexpr int JOYSTICK_Y_MIN_RAW = 0;
constexpr int JOYSTICK_Y_CENTER_RAW = 13200;
constexpr int JOYSTICK_Y_MAX_RAW = 26400;
constexpr float JOYSTICK_DEADZONE = 0.08F;

// Optional joystick button: GPIO12 (NodeMCU D6) -> button leg, GND -> other leg.
constexpr int JOYSTICK_BUTTON_PIN = 12;

// Remote mode button: GPIO13 (NodeMCU D7) -> button leg, GND -> other leg.
constexpr int REMOTE_MODE_BUTTON_PIN = 13;
constexpr unsigned long REMOTE_BUTTON_DEBOUNCE_MS = 50;
constexpr unsigned long REMOTE_BUTTON_LONG_PRESS_MS = 3000;

// Alert buzzer/speaker: GPIO14 (NodeMCU D5). For a real speaker, use a
// transistor/MOSFET driver or amplifier; do not drive a speaker directly.
constexpr int ALERT_BUZZER_PIN = 14;
constexpr bool ALERT_USE_PASSIVE_BUZZER = true;
constexpr unsigned long ALERT_PATTERN_UPDATE_INTERVAL_MS = 20;
constexpr unsigned long ALERT_PLAY_ONCE_DURATION_MS = 2500;
constexpr int ALERT_MIN_FREQUENCY_HZ = 600;
constexpr int ALERT_MAX_FREQUENCY_HZ = 1800;
constexpr int ALERT_FREQUENCY_STEP_HZ = 20;
