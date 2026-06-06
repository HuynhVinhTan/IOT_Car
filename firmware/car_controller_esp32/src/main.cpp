#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("MINIMAL_BOOT_OK");
}

void loop() {
  Serial.println("alive");
  delay(1000);
}
