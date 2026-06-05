#include "button_input.h"
#include "pin_config.h"

namespace ButtonInput {

  struct Button {
    uint8_t pin;
    bool state;
    unsigned long lastChangeTime;
  };

  static Button btnFwd = {BUTTON_1_PIN, false, 0};
  static Button btnBwd = {BUTTON_2_PIN, false, 0};
  static Button btnLft = {BUTTON_3_PIN, false, 0};
  static Button btnRgt = {BUTTON_4_PIN, false, 0};

  void init() {
    pinMode(BUTTON_1_PIN, INPUT_PULLUP);
    pinMode(BUTTON_2_PIN, INPUT_PULLUP);
    pinMode(BUTTON_3_PIN, INPUT_PULLUP);
    pinMode(BUTTON_4_PIN, INPUT_PULLUP);
  }

  static bool readDebounced(Button& b) {
    bool rawState = (digitalRead(b.pin) == LOW); // LOW means pressed
    
    if (rawState != b.state) {
      if (millis() - b.lastChangeTime > BUTTON_DEBOUNCE_MS) {
        b.state = rawState;
        b.lastChangeTime = millis();
      }
    }
    return b.state;
  }

  CommandState readState() {
    bool fwd = readDebounced(btnFwd);
    bool bwd = readDebounced(btnBwd);
    bool lft = readDebounced(btnLft);
    bool rgt = readDebounced(btnRgt);

    // If multiple contradicting directions, return STOP
    if (fwd && bwd) return CMD_STOP;
    if (lft && rgt) return CMD_STOP;
    
    // Simple priority: FWD > BWD > LFT > RGT
    if (fwd) return CMD_FORWARD;
    if (bwd) return CMD_BACKWARD;
    if (lft) return CMD_LEFT;
    if (rgt) return CMD_RIGHT;

    return CMD_STOP;
  }

}