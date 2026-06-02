#include "engine.h"

#include "pin_config.h"

void Engine::begin() {
  pinMode(LEFT_MOTOR_DIR_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_DIR_PIN, OUTPUT);

  ledcSetup(LEFT_MOTOR_PWM_CHANNEL, MOTOR_PWM_FREQUENCY_HZ,
            MOTOR_PWM_RESOLUTION_BITS);
  ledcSetup(RIGHT_MOTOR_PWM_CHANNEL, MOTOR_PWM_FREQUENCY_HZ,
            MOTOR_PWM_RESOLUTION_BITS);
  ledcAttachPin(LEFT_MOTOR_PWM_PIN, LEFT_MOTOR_PWM_CHANNEL);
  ledcAttachPin(RIGHT_MOTOR_PWM_PIN, RIGHT_MOTOR_PWM_CHANNEL);

  stop();
}

void Engine::setMotorSpeeds(int leftMotorSpeed, int rightMotorSpeed) {
  currentLeftMotorSpeed_ =
      constrain(leftMotorSpeed, MIN_MOTOR_SPEED, MAX_MOTOR_SPEED);
  currentRightMotorSpeed_ =
      constrain(rightMotorSpeed, MIN_MOTOR_SPEED, MAX_MOTOR_SPEED);

  applyMotorSpeed(currentLeftMotorSpeed_, LEFT_MOTOR_PWM_PIN,
                  LEFT_MOTOR_DIR_PIN, LEFT_MOTOR_PWM_CHANNEL,
                  LEFT_MOTOR_FORWARD_LEVEL);
  applyMotorSpeed(currentRightMotorSpeed_, RIGHT_MOTOR_PWM_PIN,
                  RIGHT_MOTOR_DIR_PIN, RIGHT_MOTOR_PWM_CHANNEL,
                  RIGHT_MOTOR_FORWARD_LEVEL);
}

void Engine::stop() {
  currentLeftMotorSpeed_ = 0;
  currentRightMotorSpeed_ = 0;
  ledcWrite(LEFT_MOTOR_PWM_CHANNEL, 0);
  ledcWrite(RIGHT_MOTOR_PWM_CHANNEL, 0);
}

int Engine::leftMotorSpeed() const {
  return currentLeftMotorSpeed_;
}

int Engine::rightMotorSpeed() const {
  return currentRightMotorSpeed_;
}

void Engine::applyMotorSpeed(int requestedSpeed, int pwmPin, int directionPin,
                             int pwmChannel, bool forwardLevel) {
  (void)pwmPin;
  const bool movingForward = requestedSpeed >= 0;
  const int pwmDuty = abs(requestedSpeed);
  const bool directionLevel = movingForward ? forwardLevel : !forwardLevel;

  digitalWrite(directionPin, directionLevel);
  ledcWrite(pwmChannel, pwmDuty);
}
