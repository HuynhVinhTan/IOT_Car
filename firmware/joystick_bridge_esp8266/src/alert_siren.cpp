#include "alert_siren.h"

#include "pin_config.h"

void AlertSiren::begin() {
  pinMode(ALERT_BUZZER_PIN, OUTPUT);
  stop();
}

void AlertSiren::start() {
  if (!enabled_) {
    stop();
    return;
  }

  active_ = true;
  playOnceMode_ = false;
}

void AlertSiren::stop() {
  active_ = false;
  playOnceMode_ = false;
  activeBuzzerLevel_ = false;
  noTone(ALERT_BUZZER_PIN);
  digitalWrite(ALERT_BUZZER_PIN, LOW);
}

void AlertSiren::playOnce(unsigned long currentTimeMs) {
  if (!enabled_) {
    stop();
    return;
  }

  active_ = true;
  playOnceMode_ = true;
  playOnceStartedMs_ = currentTimeMs;
}

void AlertSiren::setEnabled(bool enabled) {
  enabled_ = enabled;
  if (!enabled_) {
    stop();
  }
}

void AlertSiren::update(unsigned long currentTimeMs) {
  if (!active_ || !enabled_) {
    return;
  }

  if (playOnceMode_ &&
      currentTimeMs - playOnceStartedMs_ >= ALERT_PLAY_ONCE_DURATION_MS) {
    stop();
    return;
  }

  if (ALERT_USE_PASSIVE_BUZZER) {
    updateSweepTone(currentTimeMs);
  } else {
    updateActiveBuzzerPattern(currentTimeMs);
  }
}

bool AlertSiren::isActive() const {
  return active_;
}

bool AlertSiren::isEnabled() const {
  return enabled_;
}

void AlertSiren::updateSweepTone(unsigned long currentTimeMs) {
  if (lastPatternUpdateMs_ != 0 &&
      currentTimeMs - lastPatternUpdateMs_ < ALERT_PATTERN_UPDATE_INTERVAL_MS) {
    return;
  }

  currentFrequencyHz_ += ALERT_FREQUENCY_STEP_HZ * frequencyDirection_;
  if (currentFrequencyHz_ >= ALERT_MAX_FREQUENCY_HZ) {
    currentFrequencyHz_ = ALERT_MAX_FREQUENCY_HZ;
    frequencyDirection_ = -1;
  } else if (currentFrequencyHz_ <= ALERT_MIN_FREQUENCY_HZ) {
    currentFrequencyHz_ = ALERT_MIN_FREQUENCY_HZ;
    frequencyDirection_ = 1;
  }

  tone(ALERT_BUZZER_PIN, currentFrequencyHz_);
  lastPatternUpdateMs_ = currentTimeMs;
}

void AlertSiren::updateActiveBuzzerPattern(unsigned long currentTimeMs) {
  if (lastPatternUpdateMs_ != 0 &&
      currentTimeMs - lastPatternUpdateMs_ < 150) {
    return;
  }

  activeBuzzerLevel_ = !activeBuzzerLevel_;
  digitalWrite(ALERT_BUZZER_PIN, activeBuzzerLevel_ ? HIGH : LOW);
  lastPatternUpdateMs_ = currentTimeMs;
}
