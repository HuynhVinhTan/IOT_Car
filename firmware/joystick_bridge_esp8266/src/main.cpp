#include <Arduino.h>
#include "joystick_bridge_controller.h"

JoystickBridgeController joystickBridgeController;

void setup() {
  joystickBridgeController.begin();
}

void loop() {
  joystickBridgeController.update();
}
