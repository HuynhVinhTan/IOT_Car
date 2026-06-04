#include "engine.h"
#include "pin_config.h"

void Engine::begin() {
  pinMode(LEFT_MOTOR_IN1_PIN, OUTPUT);
  pinMode(LEFT_MOTOR_IN2_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_IN3_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_IN4_PIN, OUTPUT);

  ledcSetup(0, MOTOR_PWM_FREQUENCY_HZ, MOTOR_PWM_RESOLUTION_BITS);
  ledcSetup(1, MOTOR_PWM_FREQUENCY_HZ, MOTOR_PWM_RESOLUTION_BITS);
  ledcAttachPin(LEFT_MOTOR_ENA_PIN, 0);
  ledcAttachPin(RIGHT_MOTOR_ENB_PIN, 1);

  stop();
}

void Engine::setMotorSpeeds(int leftMotorSpeed, int rightMotorSpeed) {
  currentLeftMotorSpeed_ = constrain(leftMotorSpeed, MIN_MOTOR_SPEED, MAX_MOTOR_SPEED);
  currentRightMotorSpeed_ = constrain(rightMotorSpeed, MIN_MOTOR_SPEED, MAX_MOTOR_SPEED);

  // Left Motor
  if (currentLeftMotorSpeed_ > 0) {
    digitalWrite(LEFT_MOTOR_IN1_PIN, HIGH);
    digitalWrite(LEFT_MOTOR_IN2_PIN, LOW);
  } else if (currentLeftMotorSpeed_ < 0) {
    digitalWrite(LEFT_MOTOR_IN1_PIN, LOW);
    digitalWrite(LEFT_MOTOR_IN2_PIN, HIGH);
  } else {
    digitalWrite(LEFT_MOTOR_IN1_PIN, LOW);
    digitalWrite(LEFT_MOTOR_IN2_PIN, LOW);
  }
  ledcWrite(0, abs(currentLeftMotorSpeed_));

  // Right Motor
  if (currentRightMotorSpeed_ > 0) {
    digitalWrite(RIGHT_MOTOR_IN3_PIN, HIGH);
    digitalWrite(RIGHT_MOTOR_IN4_PIN, LOW);
  } else if (currentRightMotorSpeed_ < 0) {
    digitalWrite(RIGHT_MOTOR_IN3_PIN, LOW);
    digitalWrite(RIGHT_MOTOR_IN4_PIN, HIGH);
  } else {
    digitalWrite(RIGHT_MOTOR_IN3_PIN, LOW);
    digitalWrite(RIGHT_MOTOR_IN4_PIN, LOW);
  }
  ledcWrite(1, abs(currentRightMotorSpeed_));
}

void Engine::stop() {
  currentLeftMotorSpeed_ = 0;
  currentRightMotorSpeed_ = 0;
  digitalWrite(LEFT_MOTOR_IN1_PIN, LOW);
  digitalWrite(LEFT_MOTOR_IN2_PIN, LOW);
  digitalWrite(RIGHT_MOTOR_IN3_PIN, LOW);
  digitalWrite(RIGHT_MOTOR_IN4_PIN, LOW);
  ledcWrite(0, 0);
  ledcWrite(1, 0);
}

int Engine::leftMotorSpeed() const { return currentLeftMotorSpeed_; }
int Engine::rightMotorSpeed() const { return currentRightMotorSpeed_; }