#pragma once
#include <Arduino.h>

namespace AlertOutput {

  void init();
  
  // Set alert state to active (triggered by person detection event)
  void triggerAlert();
  
  // Update LED blinking and buzzer pattern. Call this frequently in loop().
  void update();

}