#include "alert_output.h"
#include "pin_config.h"

namespace AlertOutput {

  static bool alertActive = false;
  static unsigned long lastTriggerTime = 0;
  static unsigned long lastToggleTime = 0;
  static bool ledState = false; // false = LED1 ON/LED2 OFF; true = LED1 OFF/LED2 ON
  static int buzzerFreq = 800;
  static bool freqUp = true;

  void init() {
    pinMode(LED_1_PIN, OUTPUT);
    pinMode(LED_2_PIN, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);
    
    digitalWrite(LED_1_PIN, LOW);
    digitalWrite(LED_2_PIN, LOW);
    digitalWrite(BUZZER_PIN, LOW);
  }

  void triggerAlert() {
    alertActive = true;
    lastTriggerTime = millis();
  }

  void update() {
    unsigned long now = millis();

    // Check timeout
    if (alertActive && (now - lastTriggerTime > ALERT_TIMEOUT_MS)) {
      alertActive = false;
      // Turn everything off
      digitalWrite(LED_1_PIN, LOW);
      digitalWrite(LED_2_PIN, LOW);
      noTone(BUZZER_PIN);
      digitalWrite(BUZZER_PIN, LOW); // Fallback if noTone isn't used
      return;
    }

    if (alertActive) {
      // Toggle LEDs and buzzer frequency
      if (now - lastToggleTime > ALERT_LED_INTERVAL_MS) {
        lastToggleTime = now;
        ledState = !ledState;
        
        if (ledState) {
          digitalWrite(LED_1_PIN, LOW);
          digitalWrite(LED_2_PIN, HIGH);
        } else {
          digitalWrite(LED_1_PIN, HIGH);
          digitalWrite(LED_2_PIN, LOW);
        }
        
        // Passive buzzer pseudo-siren effect
        if (freqUp) {
          buzzerFreq += 200;
          if (buzzerFreq >= 1800) freqUp = false;
        } else {
          buzzerFreq -= 200;
          if (buzzerFreq <= 800) freqUp = true;
        }
        tone(BUZZER_PIN, buzzerFreq);
      }
    } else {
      // Ensure everything is off if not active
      digitalWrite(LED_1_PIN, LOW);
      digitalWrite(LED_2_PIN, LOW);
      noTone(BUZZER_PIN);
      digitalWrite(BUZZER_PIN, LOW);
    }
  }

}