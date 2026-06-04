#pragma once

// Hardware Mapping for L298N + Ultrasonic + Speed Sensors
// HC-SR04 ECHO 5V must be divided to 3.3V before entering GPIO34/35.
// L298N GND must be common with ESP32 GND.

// Ultrasonic Sensors
constexpr int RIGHT_ULTRASONIC_TRIG_PIN = 23;
constexpr int RIGHT_ULTRASONIC_ECHO_PIN = 35;
constexpr int LEFT_ULTRASONIC_TRIG_PIN = 22;
constexpr int LEFT_ULTRASONIC_ECHO_PIN = 34;
constexpr int FRONT_ULTRASONIC_TRIG_PIN = 22; // Alias
constexpr int FRONT_ULTRASONIC_ECHO_PIN = 34; // Alias
constexpr int REAR_ULTRASONIC_TRIG_PIN = 23;  // Alias
constexpr int REAR_ULTRASONIC_ECHO_PIN = 35;  // Alias

// L298N Motor Driver
// ENA/ENB must have jumpers removed if using PWM
constexpr int LEFT_MOTOR_ENA_PIN = 18;
constexpr int LEFT_MOTOR_IN1_PIN = 32;
constexpr int LEFT_MOTOR_IN2_PIN = 33;

constexpr int RIGHT_MOTOR_ENB_PIN = 19;
constexpr int RIGHT_MOTOR_IN3_PIN = 25;
constexpr int RIGHT_MOTOR_IN4_PIN = 26;

// Speed Sensors (IR FC-03 / LM393)
constexpr int SPEED_SENSOR_RIGHT_PIN = 13;
constexpr int SPEED_SENSOR_LEFT_PIN = 27;

// Other peripherals
constexpr int BATTERY_ADC_PIN = 36;
constexpr int MODE_BUTTON_PIN = 21;
constexpr int LOCAL_STATUS_BUTTON_PIN = 0; // BOOT button
constexpr int LCD_SDA_PIN = 4;
constexpr int LCD_SCL_PIN = 5;

// Battery Monitor Settings
constexpr long BATTERY_READ_INTERVAL_MS = 5000;
constexpr int ADC_MAX_VALUE = 4095;
constexpr float ADC_REFERENCE_VOLTAGE = 3.3f;
constexpr float BATTERY_VOLTAGE_DIVIDER_RATIO = 2.0f; // Assuming 1:1 divider
constexpr float BATTERY_MAX_VOLTAGE = 8.4f;
constexpr float BATTERY_MIN_VOLTAGE = 6.0f;

// Cliff Sensor Settings
constexpr int CLIFF_SENSOR_NEAR_ADC_VALUE = 500;
constexpr int CLIFF_SENSOR_FAR_ADC_VALUE = 3000;
constexpr float NORMAL_GROUND_DISTANCE_CM = 5.0f;
constexpr float CLIFF_SENSOR_MIN_DISTANCE_CM = 0.0f;
constexpr float CLIFF_SENSOR_MAX_DISTANCE_CM = 20.0f;
constexpr float CLIFF_DISTANCE_THRESHOLD_CM = 10.0f;

// Cliff Sensor Pins
constexpr int FRONT_LEFT_CLIFF_SENSOR_PIN = 39;
constexpr int FRONT_RIGHT_CLIFF_SENSOR_PIN = 38;
constexpr int REAR_LEFT_CLIFF_SENSOR_PIN = 37;
constexpr int REAR_RIGHT_CLIFF_SENSOR_PIN = 36;
constexpr bool ENABLE_FRONT_LEFT_CLIFF_SENSOR = true;
constexpr bool ENABLE_FRONT_RIGHT_CLIFF_SENSOR = true;
constexpr bool ENABLE_REAR_LEFT_CLIFF_SENSOR = true;
constexpr bool ENABLE_REAR_RIGHT_CLIFF_SENSOR = true;

// Ultrasonic Sensor Settings
constexpr bool ENABLE_FRONT_ULTRASONIC = true;
constexpr bool ENABLE_LEFT_ULTRASONIC = true;
constexpr bool ENABLE_RIGHT_ULTRASONIC = true;
constexpr bool ENABLE_REAR_ULTRASONIC = true;

// LCD Settings
constexpr int LCD_I2C_ADDRESS = 0x27;
constexpr int LCD_COLUMNS = 16;
constexpr int LCD_ROWS = 2;
constexpr long LCD_UPDATE_INTERVAL_MS = 1000;

// Button Settings
constexpr long LOCAL_BUTTON_DEBOUNCE_MS = 50;
constexpr long LOCAL_BUTTON_LONG_PRESS_MS = 2000;
constexpr long MODE_BUTTON_DEBOUNCE_MS = 50;
constexpr long MODE_BUTTON_LONG_PRESS_MS = 2000;

// WiFi and Backend Settings
constexpr char WIFI_SSID[] = "Your_WiFi_SSID";
constexpr char WIFI_PASSWORD[] = "Your_WiFi_Password";
constexpr char BACKEND_HOST[] = "192.168.1.100";
constexpr int BACKEND_PORT = 8000;
constexpr char BACKEND_WS_PATH[] = "/ws/car";