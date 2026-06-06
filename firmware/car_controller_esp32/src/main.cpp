#include <Arduino.h>
#include "car_controller.h"

CarController carController;

void setup() {
  carController.begin();
}

void loop() {
  carController.networkUpdate();
  vTaskDelay(pdMS_TO_TICKS(10));
}
