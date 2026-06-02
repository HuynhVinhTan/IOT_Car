#pragma once

#include <Arduino.h>

class RemoteModeButton {
 public:
  void begin();
  void update(unsigned long currentTimeMs);

  bool wasShortPressed();
  bool wasLongPressed();
  bool isPressed() const;

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
