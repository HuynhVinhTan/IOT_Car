#include "remote_mode_button.h"

#include "pin_config.h"

void RemoteModeButton::begin() {
  pinMode(REMOTE_MODE_BUTTON_PIN, INPUT_PULLUP);
  stablePressed_ = isPressedRaw();
  lastRawPressed_ = stablePressed_;
  stablePressedStartedMs_ = stablePressed_ ? millis() : 0;
  lastDebounceMs_ = millis();
}

void RemoteModeButton::update(unsigned long currentTimeMs) {
  const bool rawPressed = isPressedRaw();

  if (rawPressed != lastRawPressed_) {
    lastDebounceMs_ = currentTimeMs;
    lastRawPressed_ = rawPressed;
  }

  if (currentTimeMs - lastDebounceMs_ < REMOTE_BUTTON_DEBOUNCE_MS) {
    return;
  }

  if (rawPressed != stablePressed_) {
    stablePressed_ = rawPressed;
    if (stablePressed_) {
      stablePressedStartedMs_ = currentTimeMs;
      longPressAlreadyReported_ = false;
    } else {
      const unsigned long heldDurationMs =
          currentTimeMs - stablePressedStartedMs_;
      if (!longPressAlreadyReported_ &&
          heldDurationMs < REMOTE_BUTTON_LONG_PRESS_MS) {
        shortPressEventPending_ = true;
      }
      stablePressedStartedMs_ = 0;
    }
  }

  if (stablePressed_ && !longPressAlreadyReported_ &&
      currentTimeMs - stablePressedStartedMs_ >= REMOTE_BUTTON_LONG_PRESS_MS) {
    longPressEventPending_ = true;
    longPressAlreadyReported_ = true;
  }
}

bool RemoteModeButton::wasShortPressed() {
  if (!shortPressEventPending_) {
    return false;
  }

  shortPressEventPending_ = false;
  return true;
}

bool RemoteModeButton::wasLongPressed() {
  if (!longPressEventPending_) {
    return false;
  }

  longPressEventPending_ = false;
  return true;
}

bool RemoteModeButton::isPressed() const {
  return stablePressed_;
}

bool RemoteModeButton::isPressedRaw() const {
  return digitalRead(REMOTE_MODE_BUTTON_PIN) == LOW;
}
