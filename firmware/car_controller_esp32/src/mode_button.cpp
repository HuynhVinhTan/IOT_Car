#include "mode_button.h"

#include "pin_config.h"

void ModeButton::begin() {
  pinMode(MODE_BUTTON_PIN, INPUT_PULLUP);
  stablePressed_ = isPressedRaw();
  lastRawPressed_ = stablePressed_;
  shortPressEventPending_ = false;
  longPressEventPending_ = false;
  longPressAlreadyReported_ = false;
  stablePressedStartedMs_ = stablePressed_ ? millis() : 0;
  lastDebounceMs_ = millis();
}

void ModeButton::update(unsigned long currentTimeMs) {
  const bool rawPressed = isPressedRaw();

  if (rawPressed != lastRawPressed_) {
    lastDebounceMs_ = currentTimeMs;
    lastRawPressed_ = rawPressed;
  }

  if (currentTimeMs - lastDebounceMs_ < MODE_BUTTON_DEBOUNCE_MS) {
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
          heldDurationMs < MODE_BUTTON_LONG_PRESS_MS) {
        shortPressEventPending_ = true;
      }
      stablePressedStartedMs_ = 0;
    }
  }

  if (stablePressed_ && !longPressAlreadyReported_ &&
      currentTimeMs - stablePressedStartedMs_ >= MODE_BUTTON_LONG_PRESS_MS) {
    longPressEventPending_ = true;
    longPressAlreadyReported_ = true;
  }
}

bool ModeButton::wasShortPressed() {
  if (!shortPressEventPending_) {
    return false;
  }

  shortPressEventPending_ = false;
  return true;
}

bool ModeButton::wasLongPressed() {
  if (!longPressEventPending_) {
    return false;
  }

  longPressEventPending_ = false;
  return true;
}

bool ModeButton::isPressedRaw() const {
  return digitalRead(MODE_BUTTON_PIN) == LOW;
}
