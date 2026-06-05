#pragma once
#include <Arduino.h>

// ── Button Pins (INPUT_PULLUP, active LOW) ──
static constexpr uint8_t BUTTON_1_PIN = D1; // FORWARD
static constexpr uint8_t BUTTON_2_PIN = D2; // BACKWARD
static constexpr uint8_t BUTTON_3_PIN = D5; // LEFT
static constexpr uint8_t BUTTON_4_PIN = D6; // RIGHT

// ── Buzzer Pin ──
static constexpr uint8_t BUZZER_PIN = D7;

// ── LED Pins ──
// WARNING: D0/GPIO16 - no interrupt, OK for output
// WARNING: D8/GPIO15 - bootstrap pin, must not be HIGH at boot
static constexpr uint8_t LED_1_PIN = D0;
static constexpr uint8_t LED_2_PIN = D8;

// ── Timing Constants ──
static constexpr unsigned long BUTTON_DEBOUNCE_MS       = 50;
static constexpr unsigned long COMMAND_SEND_INTERVAL_MS  = 100;
static constexpr unsigned long ALERT_LED_INTERVAL_MS     = 200;
static constexpr unsigned long ALERT_TIMEOUT_MS          = 3000;
static constexpr unsigned long WIFI_RECONNECT_INTERVAL_MS = 5000;
static constexpr unsigned long WS_RECONNECT_INTERVAL_MS  = 3000;