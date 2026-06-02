#pragma once

#include <Arduino.h>
#include "car_types.h"

class Engine {
 public:
  void begin();
  void setMotorSpeeds(int leftMotorSpeed, int rightMotorSpeed);
  void stop();

  int leftMotorSpeed() const;
  int rightMotorSpeed() const;

 private:
  void applyMotorSpeed(int requestedSpeed, int pwmPin, int directionPin,
                       int pwmChannel, bool forwardLevel);

  int currentLeftMotorSpeed_ = 0;
  int currentRightMotorSpeed_ = 0;
};
