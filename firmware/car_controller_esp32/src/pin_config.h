#pragma once

// TODO: Update these pins to match the real car wiring before driving the car.

// HC-SR04 Echo is commonly 5V. Use a divider/level shifter before ESP32 GPIO.
// Avoid GPIO 21/22 here because they are reserved for the default I2C LCD bus.
constexpr bool ENABLE_FRONT_ULTRASONIC = true;
constexpr bool ENABLE_LEFT_ULTRASONIC = true;
constexpr bool ENABLE_RIGHT_ULTRASONIC = true;
constexpr bool ENABLE_REAR_ULTRASONIC = true;

constexpr int FRONT_ULTRASONIC_TRIG_PIN = 5;
constexpr int FRONT_ULTRASONIC_ECHO_PIN = 18;

constexpr int LEFT_ULTRASONIC_TRIG_PIN = 17;
constexpr int LEFT_ULTRASONIC_ECHO_PIN = 16;

constexpr int RIGHT_ULTRASONIC_TRIG_PIN = 19;
constexpr int RIGHT_ULTRASONIC_ECHO_PIN = 4;

constexpr int REAR_ULTRASONIC_TRIG_PIN = 33;
constexpr int REAR_ULTRASONIC_ECHO_PIN = 36;


// Default assumption: each motor has one PWM pin and one direction pin.
// If your driver is L298N with two direction pins per motor, update Engine
// and this file together instead of hard-coding pins elsewhere.
constexpr int LEFT_MOTOR_PWM_PIN = 25;
constexpr int LEFT_MOTOR_DIR_PIN = 26;
constexpr int RIGHT_MOTOR_PWM_PIN = 27;
constexpr int RIGHT_MOTOR_DIR_PIN = 14;

constexpr int SPEED_SENSOR_PIN = 32;

// Two-pin mode button wiring:
// GPIO -> button leg, GND -> other button leg, input uses INPUT_PULLUP.
constexpr int MODE_BUTTON_PIN = 23;
constexpr unsigned long MODE_BUTTON_DEBOUNCE_MS = 50;
constexpr unsigned long MODE_BUTTON_LONG_PRESS_MS = 5000;
constexpr int LOCAL_STATUS_BUTTON_PIN = MODE_BUTTON_PIN;
constexpr unsigned long LOCAL_BUTTON_DEBOUNCE_MS = MODE_BUTTON_DEBOUNCE_MS;
constexpr unsigned long LOCAL_BUTTON_LONG_PRESS_MS = MODE_BUTTON_LONG_PRESS_MS;

// LCD default: I2C LCD 16x2. Common addresses are 0x27 and 0x3F.
// TODO: Change LCD_I2C_ADDRESS to 0x3F if your backpack uses that address.
constexpr int LCD_SDA_PIN = 21;
constexpr int LCD_SCL_PIN = 22;
constexpr uint8_t LCD_I2C_ADDRESS = 0x27;
constexpr int LCD_COLUMNS = 16;
constexpr int LCD_ROWS = 2;
constexpr unsigned long LCD_UPDATE_INTERVAL_MS = 500;

// Battery ADC input. The battery voltage must go through a voltage divider.
// Never connect a battery above 3.3V directly to ESP32 ADC.
constexpr int BATTERY_ADC_PIN = 34;
constexpr unsigned long BATTERY_READ_INTERVAL_MS = 1000;
constexpr float ADC_REFERENCE_VOLTAGE = 3.3F;
constexpr int ADC_MAX_VALUE = 4095;

// TODO: Update these values for the real divider and battery chemistry.
constexpr float BATTERY_VOLTAGE_DIVIDER_RATIO = 2.0F;
constexpr float BATTERY_MIN_VOLTAGE = 6.4F;
constexpr float BATTERY_MAX_VOLTAGE = 8.4F;

// Cliff/drop-off sensors. Analog IR sensors are used as the MVP assumption.
// For VL53L0X/VL53L1X ToF sensors, replace CliffSensor internals and keep the
// array/controller interfaces stable.
constexpr bool ENABLE_FRONT_LEFT_CLIFF_SENSOR = true;
constexpr bool ENABLE_FRONT_RIGHT_CLIFF_SENSOR = true;
constexpr bool ENABLE_REAR_LEFT_CLIFF_SENSOR = false;
constexpr bool ENABLE_REAR_RIGHT_CLIFF_SENSOR = false;

constexpr int FRONT_LEFT_CLIFF_SENSOR_PIN = 35;
constexpr int FRONT_RIGHT_CLIFF_SENSOR_PIN = 39;

// TODO: Update rear cliff pins before enabling rear sensors. GPIO12/GPIO15 are
// boot-strapping/ADC2 pins on many ESP32 boards; validate your board wiring.
constexpr int REAR_LEFT_CLIFF_SENSOR_PIN = 12;
constexpr int REAR_RIGHT_CLIFF_SENSOR_PIN = 15;

constexpr float NORMAL_GROUND_DISTANCE_CM = 5.0F;
constexpr float CLIFF_DISTANCE_THRESHOLD_CM = 12.0F;
constexpr float CLIFF_SENSOR_MIN_DISTANCE_CM = 2.0F;
constexpr float CLIFF_SENSOR_MAX_DISTANCE_CM = 30.0F;
constexpr int CLIFF_SENSOR_NEAR_ADC_VALUE = 3200;
constexpr int CLIFF_SENSOR_FAR_ADC_VALUE = 800;

// WiFi and Backend Settings
constexpr char WIFI_SSID[] = "Your_WiFi_SSID";
constexpr char WIFI_PASSWORD[] = "Your_WiFi_Password";
constexpr char BACKEND_HOST[] = "192.168.1.100"; // Adjust to your PC's IP
constexpr int BACKEND_PORT = 8000;
constexpr char BACKEND_WS_PATH[] = "/ws/car";

