#pragma once
#include <Arduino.h>

namespace ButtonInput {

  enum CommandState {
    CMD_STOP,
    CMD_FORWARD,
    CMD_BACKWARD,
    CMD_LEFT,
    CMD_RIGHT
  };

  void init();
  
  // Read current button state, handling debounce
  // Prioritizes multiple presses (e.g., if forward + left are pressed, picks one logically or returns STOP)
  CommandState readState();
  
}