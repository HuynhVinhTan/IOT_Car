#pragma once

#include <Arduino.h>

class AlertSiren {
 public:
  void begin();
  void start();
  void stop();
  void playOnce(unsigned long currentTimeMs);
  void setEnabled(bool enabled);
  void update(unsigned long currentTimeMs);
  bool isActive() const;
  bool isEnabled() const;

 private:
  void updateSweepTone(unsigned long currentTimeMs);
  void updateActiveBuzzerPattern(unsigned long currentTimeMs);

  bool enabled_ = true;
  bool active_ = false;
  bool playOnceMode_ = false;
  bool activeBuzzerLevel_ = false;
  int currentFrequencyHz_ = 600;
  int frequencyDirection_ = 1;
  unsigned long playOnceStartedMs_ = 0;
  unsigned long lastPatternUpdateMs_ = 0;
};
