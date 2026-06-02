#pragma once

#include <Arduino.h>
#include <PCF8574.h>
#include "joystick_types.h"

// Forward declaration
class RouteButtonController {
 public:
  RouteButtonController();
  
  bool begin(TwoWire* wire = &Wire);
  void update(unsigned long currentTimeMs);
  bool isAvailable() const;
  bool hasEvent() const;
  RouteButtonEvent consumeEvent();

 private:
  PCF8574 pcf8574_;
  bool available_;
  
  bool prevPressed_;
  bool nextPressed_;
  bool confirmPressed_;

  unsigned long prevPressTime_;
  unsigned long nextPressTime_;
  unsigned long confirmPressTime_;

  bool prevReported_;
  bool nextReported_;
  bool confirmReportedShort_;
  bool confirmReportedLong_;

  bool hasEvent_;
  RouteButtonEvent currentEvent_;
  
  void readPins();
  void enqueueEvent(RouteButtonEventType type, unsigned long timestamp);
};
