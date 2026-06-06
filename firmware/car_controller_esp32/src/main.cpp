#include <Arduino.h>
#include <WiFi.h>
#include "esp_system.h"
#include "esp_wifi.h"
#include "app_config.h"

#define FIRMWARE_BUILD_MARKER "WIFI_RUNTIME_VERIFY_2026_06_06"
#define WIFI_RECONNECT_INTERVAL_MS 30000  // 30 seconds

AppConfig appConfig;
unsigned long lastWifiCheck = 0;
unsigned long lastHeartbeat = 0;
unsigned long bootTime = 0;
bool wifiConnected = false;

void print_reset_reason() {
    esp_reset_reason_t reason = esp_reset_reason();
    Serial.print("Reset reason: ");
    switch (reason) {
        case ESP_RST_POWERON: Serial.println("POWERON_RESET"); break;
        case ESP_RST_EXT: Serial.println("EXTERNAL_RESET"); break;
        case ESP_RST_SW: Serial.println("SOFTWARE_RESET"); break;
        case ESP_RST_PANIC: Serial.println("PANIC_RESET"); break;
        case ESP_RST_INT_WDT: Serial.println("INT_WDT_RESET"); break;
        case ESP_RST_TASK_WDT: Serial.println("TASK_WDT_RESET"); break;
        case ESP_RST_WDT: Serial.println("WDT_RESET"); break;
        case ESP_RST_DEEPSLEEP: Serial.println("DEEPSLEEP_RESET"); break;
        case ESP_RST_BROWNOUT: Serial.println("BROWNOUT_RESET"); break;
        case ESP_RST_SDIO: Serial.println("SDIO_RESET"); break;
        default: Serial.println("UNKNOWN"); break;
    }
}

void print_wifi_status() {
    wl_status_t status = WiFi.status();
    Serial.print("WiFi status: ");
    switch (status) {
        case WL_IDLE_STATUS: Serial.print("IDLE"); break;
        case WL_NO_SSID_AVAIL: Serial.print("NO_SSID"); break;
        case WL_SCAN_COMPLETED: Serial.print("SCAN_COMPLETED"); break;
        case WL_CONNECTED: Serial.print("CONNECTED"); break;
        case WL_CONNECT_FAILED: Serial.print("CONNECT_FAILED"); break;
        case WL_CONNECTION_LOST: Serial.print("CONNECTION_LOST"); break;
        case WL_DISCONNECTED: Serial.print("DISCONNECTED"); break;
        default: Serial.print("UNKNOWN"); break;
    }
    
    if (status == WL_CONNECTED) {
        Serial.printf(" | IP: %s | RSSI: %d dBm", 
                     WiFi.localIP().toString().c_str(), 
                     WiFi.RSSI());
    }
    Serial.println();
}

void connect_wifi() {
    if (appConfig.wifiSsid.length() == 0) {
        Serial.println("ERROR: No WiFi SSID configured");
        return;
    }

    Serial.printf("Connecting to WiFi SSID: %s\n", appConfig.wifiSsid.c_str());
    
    WiFi.mode(WIFI_STA);
    WiFi.persistent(false);
    WiFi.setSleep(false);
    WiFi.setAutoReconnect(true);
    
    WiFi.begin(appConfig.wifiSsid.c_str(), appConfig.wifiPassword.c_str());
    
    int timeout = 0;
    while (WiFi.status() != WL_CONNECTED && timeout < 20) {
        delay(500);
        Serial.print(".");
        timeout++;
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        wifiConnected = true;
        Serial.println("✓ WiFi connected!");
        Serial.printf("  IP address: %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("  RSSI: %d dBm\n", WiFi.RSSI());
        Serial.printf("  Gateway: %s\n", WiFi.gatewayIP().toString().c_str());
    } else {
        wifiConnected = false;
        Serial.println("✗ WiFi connection failed");
        print_wifi_status();
    }
}

void check_wifi_connection() {
    unsigned long now = millis();
    
    // Check WiFi status
    wl_status_t status = WiFi.status();
    bool currentlyConnected = (status == WL_CONNECTED);
    
    // Detect state change
    if (currentlyConnected != wifiConnected) {
        if (currentlyConnected) {
            Serial.println("✓ WiFi reconnected!");
            Serial.printf("  IP address: %s\n", WiFi.localIP().toString().c_str());
            wifiConnected = true;
        } else {
            Serial.println("✗ WiFi connection lost!");
            print_wifi_status();
            wifiConnected = false;
        }
    }
    
    // If not connected and enough time has passed, try to reconnect
    if (!wifiConnected && (now - lastWifiCheck >= WIFI_RECONNECT_INTERVAL_MS)) {
        lastWifiCheck = now;
        Serial.println("Attempting WiFi reconnection...");
        connect_wifi();
    }
}

void print_heartbeat() {
    unsigned long now = millis();
    if (now - lastHeartbeat >= 1000) {
        lastHeartbeat = now;
        unsigned long uptime = (now - bootTime) / 1000;  // seconds
        Serial.printf("[%lu s] alive | heap: %d | ", uptime, ESP.getFreeHeap());
        print_wifi_status();
    }
}

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    bootTime = millis();
    
    Serial.println("\n\n========================================");
    Serial.println(FIRMWARE_BUILD_MARKER);
    Serial.println("========================================");
    
    print_reset_reason();
    Serial.printf("Free heap: %d bytes\n", ESP.getFreeHeap());
    Serial.printf("Chip model: %s\n", ESP.getChipModel());
    Serial.printf("CPU frequency: %d MHz\n", ESP.getCpuFreqMHz());
    
    // Load configuration from preferences
    Serial.println("\nLoading configuration from NVS...");
    loadConfig(appConfig);
    printConfig(appConfig);
    
    if (!appConfig.valid) {
        Serial.println("\n✗ ERROR: Configuration is invalid!");
        Serial.println("Please configure WiFi and backend settings via config portal");
        Serial.println("Continuing with limited functionality...");
    }
    
    // Attempt initial WiFi connection
    if (appConfig.wifiSsid.length() > 0) {
        Serial.println("\nInitializing WiFi...");
        connect_wifi();
    } else {
        Serial.println("\n✗ No WiFi credentials configured");
    }
    
    lastWifiCheck = millis();
    lastHeartbeat = millis();
    
    Serial.println("\n========================================");
    Serial.println("Setup complete. Entering main loop...");
    Serial.println("========================================\n");
}

void loop() {
    // Print heartbeat every second
    print_heartbeat();
    
    // Check WiFi connection and reconnect if needed
    check_wifi_connection();
    
    delay(100);  // Small delay to prevent tight loop
}