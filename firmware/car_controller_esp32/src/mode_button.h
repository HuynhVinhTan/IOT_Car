#pragma once

#include <Arduino.h>

class ModeButton {
 public:
  void begin();
  void update(unsigned long currentTimeMs);
  bool wasShortPressed();
  bool wasLongPressed();

 private:
  bool isPressedRaw() const;

  bool stablePressed_ = false;
  bool lastRawPressed_ = false;
  bool shortPressEventPending_ = false;
  bool longPressEventPending_ = false;
  bool longPressAlreadyReported_ = false;
  unsigned long stablePressedStartedMs_ = 0;
  unsigned long lastDebounceMs_ = 0;
};
