#include "route_button_controller.h"
#include "pin_config.h"

RouteButtonController::RouteButtonController()
    : pcf8574_(PCF8574_I2C_ADDRESS),
      available_(false),
      prevPressed_(false),
      nextPressed_(false),
      confirmPressed_(false),
      prevPressTime_(0),
      nextPressTime_(0),
      confirmPressTime_(0),
      prevReported_(false),
      nextReported_(false),
      confirmReportedShort_(false),
      confirmReportedLong_(false),
      hasEvent_(false) {}

bool RouteButtonController::begin(TwoWire* wire) {
  if (!pcf8574_.begin()) {
    available_ = false;
    Serial.println("PCF8574 not found. Route buttons unavailable.");
    return false;
  }
  available_ = true;
  // Initialize pins as inputs with internal pullups if the chip supports,
  // PCF8574 generally expects pins written HIGH to act as inputs with weak pullup.
  for (uint8_t i = 0; i < 8; i++) {
    pcf8574_.write(i, HIGH);
  }
  return true;
}

bool RouteButtonController::isAvailable() const { return available_; }

bool RouteButtonController::hasEvent() const { return hasEvent_; }

RouteButtonEvent RouteButtonController::consumeEvent() {
  hasEvent_ = false;
  return currentEvent_;
}

void RouteButtonController::enqueueEvent(RouteButtonEventType type,
                                         unsigned long timestamp) {
  if (hasEvent_) {
    return; // Drop if not consumed. Simple MVP.
  }
  currentEvent_.type = type;
  currentEvent_.timestampMs = timestamp;
  hasEvent_ = true;
}

void RouteButtonController::update(unsigned long currentTimeMs) {
  if (!available_ || hasEvent_) {
    return;
  }

  // PCF8574 read: pins pulled to GND means active (LOW == pressed)
  uint8_t val = pcf8574_.read8();
  bool currentPrev = (val & (1 << PCF_PIN_ROUTE_PREV)) == 0;
  bool currentNext = (val & (1 << PCF_PIN_ROUTE_NEXT)) == 0;
  bool currentConfirm = (val & (1 << PCF_PIN_ROUTE_CONFIRM)) == 0;

  // Previous button
  if (currentPrev && !prevPressed_) {
    prevPressed_ = true;
    prevPressTime_ = currentTimeMs;
    prevReported_ = false;
  } else if (!currentPrev && prevPressed_) {
    if (!prevReported_ && (currentTimeMs - prevPressTime_ > ROUTE_BUTTON_DEBOUNCE_MS)) {
      enqueueEvent(RouteButtonEventType::PreviousSegment, currentTimeMs);
      prevReported_ = true;
    }
    prevPressed_ = false;
  }

  // Next button
  if (currentNext && !nextPressed_) {
    nextPressed_ = true;
    nextPressTime_ = currentTimeMs;
    nextReported_ = false;
  } else if (!currentNext && nextPressed_) {
    if (!nextReported_ && (currentTimeMs - nextPressTime_ > ROUTE_BUTTON_DEBOUNCE_MS)) {
      enqueueEvent(RouteButtonEventType::NextSegment, currentTimeMs);
      nextReported_ = true;
    }
    nextPressed_ = false;
  }

  // Confirm button (short = Confirm, long = AutoInfer)
  if (currentConfirm && !confirmPressed_) {
    confirmPressed_ = true;
    confirmPressTime_ = currentTimeMs;
    confirmReportedShort_ = false;
    confirmReportedLong_ = false;
  } else if (currentConfirm && confirmPressed_) {
    if (!confirmReportedLong_ && 
        (currentTimeMs - confirmPressTime_ > ROUTE_BUTTON_LONG_PRESS_MS)) {
      enqueueEvent(RouteButtonEventType::AutoInferSegment, currentTimeMs);
      confirmReportedLong_ = true;
    }
  } else if (!currentConfirm && confirmPressed_) {
    // Release
    if (!confirmReportedLong_ && !confirmReportedShort_ && 
        (currentTimeMs - confirmPressTime_ > ROUTE_BUTTON_DEBOUNCE_MS)) {
      enqueueEvent(RouteButtonEventType::ConfirmSegment, currentTimeMs);
      confirmReportedShort_ = true;
    }
    confirmPressed_ = false;
  }
}
