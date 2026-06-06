#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("MINIMAL_BOOT_OK");
}

void loop() {
  carController.networkUpdate();
  vTaskDelay(pdMS_TO_TICKS(10));
}
