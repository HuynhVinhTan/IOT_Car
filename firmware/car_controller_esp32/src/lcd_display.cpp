#include "lcd_display.h"

#include <Wire.h>
#include "pin_config.h"

LcdDisplay::LcdDisplay() : lcd_(LCD_I2C_ADDRESS, LCD_COLUMNS, LCD_ROWS) {}

void LcdDisplay::begin() {
  Wire.begin(LCD_SDA_PIN, LCD_SCL_PIN);
  lcd_.init();
  available_ = true;
  turnOn();
  printPaddedLine(0, "Smart Car");
  printPaddedLine(1, "LCD ready");
}

void LcdDisplay::turnOn() {
  if (!available_ || enabled_) {
    return;
  }

  lcd_.backlight();
  enabled_ = true;
  latestLine1_ = "";
  latestLine2_ = "";
}

void LcdDisplay::turnOff() {
  if (!available_ || !enabled_) {
    return;
  }

  lcd_.noBacklight();
  enabled_ = false;
}

bool LcdDisplay::isEnabled() const {
  return enabled_;
}

void LcdDisplay::updateStatus(DriveMode currentDriveMode, int batteryPercent,
                              float batteryVoltage, const char* currentNode,
                              bool obstacleDetected, bool cliffDetected,
                              bool personDetected,
                              const char* emergencyReason,
                              unsigned long currentTimeMs) {
  if (!available_ || !enabled_) {
    return;
  }

  if (lastUpdateMs_ != 0 &&
      currentTimeMs - lastUpdateMs_ < LCD_UPDATE_INTERVAL_MS) {
    return;
  }

  if (currentDriveMode == DriveMode::EmergencyStop) {
    renderEmergencyStatus(emergencyReason, batteryPercent);
  } else if (personDetected) {
    renderAiAlert(batteryPercent, currentNode);
  } else {
    renderNormalStatus(currentDriveMode, batteryPercent, batteryVoltage,
                       currentNode, obstacleDetected, cliffDetected);
  }

  lastUpdateMs_ = currentTimeMs;
}

const char* LcdDisplay::status() const {
  if (!available_) {
    return "UNAVAILABLE";
  }

  return enabled_ ? "ON" : "OFF";
}

void LcdDisplay::renderNormalStatus(DriveMode currentDriveMode,
                                    int batteryPercent,
                                    float batteryVoltage,
                                    const char* currentNode,
                                    bool obstacleDetected,
                                    bool cliffDetected) {
  String line1 = String("Mode: ") + driveModeToString(currentDriveMode);
  if (line1.length() > LCD_COLUMNS) {
    line1 = driveModeToString(currentDriveMode);
  }
  String line2 = String("Bat ") + batteryPercent + "% " +
                 String(batteryVoltage, 1) + "V";
  if (cliffDetected) {
    line2 = "CLIFF DETECTED";
  } else if (obstacleDetected) {
    line2 = "Obstacle near";
  } else if (currentNode != nullptr && strlen(currentNode) > 0) {
    line2 = String("Node: ") + currentNode;
  }

  printPaddedLine(0, line1);
  printPaddedLine(1, line2);
}

void LcdDisplay::renderEmergencyStatus(const char* emergencyReason,
                                       int batteryPercent) {
  printPaddedLine(0, "EMERGENCY STOP");
  if (emergencyReason != nullptr && strlen(emergencyReason) > 0) {
    printPaddedLine(1, emergencyReason);
  } else {
    printPaddedLine(1, String("Battery: ") + batteryPercent + "%");
  }
}

void LcdDisplay::renderAiAlert(int batteryPercent, const char* currentNode) {
  printPaddedLine(0, "PERSON FOUND");
  if (currentNode != nullptr && strlen(currentNode) > 0) {
    printPaddedLine(1, String("Node: ") + currentNode);
  } else {
    printPaddedLine(1, String("Battery: ") + batteryPercent + "%");
  }
}

void LcdDisplay::printPaddedLine(uint8_t row, const String& text) {
  String paddedText = text;
  if (paddedText.length() > LCD_COLUMNS) {
    paddedText = paddedText.substring(0, LCD_COLUMNS);
  }

  while (paddedText.length() < LCD_COLUMNS) {
    paddedText += ' ';
  }

  if (row == 0 && paddedText == latestLine1_) {
    return;
  }

  if (row == 1 && paddedText == latestLine2_) {
    return;
  }

  lcd_.setCursor(0, row);
  lcd_.print(paddedText);

  if (row == 0) {
    latestLine1_ = paddedText;
  } else if (row == 1) {
    latestLine2_ = paddedText;
  }
}
