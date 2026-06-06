#include "car_controller.h"
#include "pin_config.h"
#include "app_config.h"
#include "config_portal.h"

// Singleton pointer for callbacks
CarController* g_carController = nullptr;

CarController::CarController() :
    engine_(new Engine()),
    distanceSensorArray_(new DistanceSensorArray()),
    cliffSensorArray_(new CliffSensorArray()),
    leftSpeedSensor_(new SpeedSensor(SPEED_SENSOR_LEFT_PIN)),
    rightSpeedSensor_(new SpeedSensor(SPEED_SENSOR_RIGHT_PIN)),
    localStatusButton_(new LocalStatusButton()),
    batteryMonitor_(new BatteryMonitor()),
    lcdDisplay_(new LcdDisplay()),
    commandParser_(new CommandParser()),
    telemetryPublisher_(new TelemetryPublisher()),
    safetyGuard_(new SafetyGuard()),
    webSocket_(new WebSocketsClient()) {}

void CarController::begin() {
  g_carController = this;
  stateMutex_ = xSemaphoreCreateMutex();
  telemetryQueue_ = xQueueCreate(10, sizeof(char*));
  
  Serial.begin(115200);
  
  pinMode(MODE_HOLD_BUTTON_PIN, INPUT_PULLUP);
  
  AppConfig config;
  loadConfig(config);
  
  if (config.valid) {
    Serial.println("Valid config found. Connecting to WiFi...");
    printConfig(config);
    setupWiFi(config);
    setupWebsocket(config);
  } else {
    Serial.println("No valid config found. Starting Config Portal...");
    ConfigPortal::start();
  }

  telemetryPublisher_->begin(Serial);
  telemetryPublisher_->setJsonCallback([](const String& json) {
      if (g_carController && g_carController->telemetryQueue_) {
          char* msg = strdup(json.c_str());
          if (xQueueSend(g_carController->telemetryQueue_, &msg, 0) != pdPASS) {
              free(msg);
          }
      }
  });

  engine_->begin();
  distanceSensorArray_->begin();
  leftSpeedSensor_->begin();
  rightSpeedSensor_->begin();
  localStatusButton_->begin();
  lcdDisplay_->begin();

  const unsigned long nowMs = millis();
  lastCommandMs_ = nowMs;
  lastRemoteDriveCommandMs_ = nowMs;

  xTaskCreatePinnedToCore(
      CarController::hardwareTaskCode,
      "HardwareTask",
      4096,
      this,
      5,
      &hardwareTaskHandle_,
      1); // Core 1

  xSemaphoreTake(stateMutex_, portMAX_DELAY);
  telemetryPublisher_->publishEvent("boot", "Car firmware started (WiFi enabled)");
  xSemaphoreGive(stateMutex_);
}

void CarController::setupWiFi(const AppConfig& config) {
  Serial.print("Connecting to WiFi: ");
  Serial.println(config.wifiSsid);
  
  WiFi.begin(config.wifiSsid.c_str(), config.wifiPassword.c_str());
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void CarController::setupWebsocket(const AppConfig& config) {
  if (config.backendTls) {
    webSocket_->beginSSL(config.backendHost.c_str(), config.backendPort, BACKEND_WS_PATH);
  } else {
    webSocket_->begin(config.backendHost.c_str(), config.backendPort, BACKEND_WS_PATH);
  }
  webSocket_->onEvent([this](WStype_t type, uint8_t * payload, size_t length) {
    this->onWebsocketEvent(type, payload, length);
  });
  webSocket_->setReconnectInterval(5000);
}

void CarController::onWebsocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("[WS] Disconnected");
      break;
    case WStype_CONNECTED:
      Serial.println("[WS] Connected to Backend");
      xSemaphoreTake(stateMutex_, portMAX_DELAY);
      telemetryPublisher_->publishEvent("ws_connected", "WebSocket connection established");
      xSemaphoreGive(stateMutex_);
      break;
    case WStype_TEXT: {
      String cmd = String((char*)payload);
      const ParsedCommand parsedCommand = commandParser_->parseLine(cmd);
      handleCommand(parsedCommand);
      break;
    }
    default:
      break;
  }
}

void CarController::hardwareTaskCode(void* parameter) {
  CarController* instance = static_cast<CarController*>(parameter);
  while (true) {
    instance->hardwareUpdate();
    vTaskDelay(pdMS_TO_TICKS(10));
  }
}

void CarController::networkUpdate() {
  webSocket_->loop();
  
  char* msg = nullptr;
  while (xQueueReceive(telemetryQueue_, &msg, 0) == pdTRUE) {
    if (webSocket_->isConnected()) {
      webSocket_->sendTXT(msg);
    }
    free(msg);
  }
}

void CarController::hardwareUpdate() {
  const unsigned long nowMs = millis();

  localStatusButton_->update(nowMs);
  leftSpeedSensor_->update(nowMs);
  rightSpeedSensor_->update(nowMs);
  updateSensorsIfDue(nowMs);

  xSemaphoreTake(stateMutex_, portMAX_DELAY);

  if (localStatusButton_->wasLongPressed()) {
    handleModeButtonLongPress();
  } else if (localStatusButton_->wasShortPressed()) {
    handleModeButtonShortPress();
  }

  // Mode Hold Button Logic
  if (digitalRead(MODE_HOLD_BUTTON_PIN) == LOW) {
    if (modeHoldStartTime_ == 0) {
      modeHoldStartTime_ = nowMs;
    } else if (!modeHoldTriggered_ && (nowMs - modeHoldStartTime_ >= MODE_HOLD_THRESHOLD_MS)) {
      enterManualRemoteMode("mode button hold");
      modeHoldTriggered_ = true;
    }
  } else {
    modeHoldStartTime_ = 0;
    modeHoldTriggered_ = false;
  }

  if (currentDriveMode_ == DriveMode::EmergencyStop) {
    engine_->stop();
  } else if (currentDriveMode_ == DriveMode::ManualRemote ||
             currentDriveMode_ == DriveMode::LearningMap) {
    updateManualRemoteMode(nowMs);
  } else {
    engine_->stop();
  }

  updateLocalDisplay(nowMs);
  publishTelemetryIfDue(nowMs);

  xSemaphoreGive(stateMutex_);
}

void CarController::handleCommand(const ParsedCommand& parsedCommand) {
  const unsigned long nowMs = millis();
  
  xSemaphoreTake(stateMutex_, portMAX_DELAY);
  lastCommandMs_ = nowMs;

  if (!parsedCommand.valid) {
    telemetryPublisher_->publishCommandAck(parsedCommand.commandName, false,
                                          parsedCommand.errorMessage);
    xSemaphoreGive(stateMutex_);
    return;
  }

  if (currentDriveMode_ == DriveMode::EmergencyStop &&
      !commandAllowedInEmergency(parsedCommand.type)) {
    telemetryPublisher_->publishCommandAck(
        parsedCommand.commandName, false,
        "Emergency stop active. Send RESET_EMERGENCY");
    xSemaphoreGive(stateMutex_);
    return;
  }

  switch (parsedCommand.type) {
    case CommandType::SetMode:
      handleSetModeCommand(parsedCommand.requestedMode);
      break;
    case CommandType::RemoteDrive:
      handleRemoteDriveCommand(parsedCommand, nowMs);
      break;
    case CommandType::RemoteStop:
      desiredMotorSpeeds_ = MotorSpeeds();
      effectiveMotorSpeeds_ = MotorSpeeds();
      lastRemoteDriveCommandMs_ = nowMs;
      remoteCommandTimedOut_ = false;
      engine_->stop();
      telemetryPublisher_->publishCommandAck(parsedCommand.commandName, true, "Remote stop");
      break;
    case CommandType::EmergencyStop:
      enterEmergencyStop("Commanded emergency stop");
      telemetryPublisher_->publishCommandAck(parsedCommand.commandName, true, "E-Stop engaged");
      break;
    case CommandType::ResetEmergency:
      emergencyStopReason_ = "";
      enterIdleMode("Emergency reset");
      telemetryPublisher_->publishCommandAck(parsedCommand.commandName, true, "E-Stop reset");
      break;
    case CommandType::PersonDetected:
      personDetectedByAi_ = parsedCommand.personDetected;
      if (personDetectedByAi_ && STOP_ON_PERSON_DETECTED) {
        enterEmergencyStop("Person detected by AI");
      }
      telemetryPublisher_->publishCommandAck(parsedCommand.commandName, true, "Person detected update");
      break;
    case CommandType::PersonLost:
      personDetectedByAi_ = false;
      telemetryPublisher_->publishCommandAck(parsedCommand.commandName, true, "Person lost update");
      break;
    default:
      telemetryPublisher_->publishCommandAck(parsedCommand.commandName, false, "Unsupported or legacy command");
      break;
  }
  xSemaphoreGive(stateMutex_);
}

void CarController::handleSetModeCommand(DriveMode requestedMode) {
  if (requestedMode == DriveMode::Idle) {
    enterIdleMode("Mode set to IDLE");
    telemetryPublisher_->publishCommandAck("SET_MODE", true, "Mode: IDLE");
  } else if (requestedMode == DriveMode::ManualRemote) {
    enterManualRemoteMode("Mode set to MANUAL_REMOTE");
    telemetryPublisher_->publishCommandAck("SET_MODE", true, "Mode: MANUAL_REMOTE");
  } else if (requestedMode == DriveMode::StatusDisplay) {
    enterStatusDisplayMode("Mode set to STATUS_DISPLAY");
    telemetryPublisher_->publishCommandAck("SET_MODE", true, "Mode: STATUS_DISPLAY");
  } else if (requestedMode == DriveMode::EmergencyStop) {
    enterEmergencyStop("Mode set to E-STOP");
    telemetryPublisher_->publishCommandAck("SET_MODE", true, "Mode: E-STOP");
  } else {
     telemetryPublisher_->publishCommandAck("SET_MODE", false, "Mode not supported in WiFi firmware");
  }
}

void CarController::handleRemoteDriveCommand(const ParsedCommand& parsedCommand, unsigned long nowMs) {
  if (currentDriveMode_ != DriveMode::ManualRemote && currentDriveMode_ != DriveMode::LearningMap) {
    telemetryPublisher_->publishCommandAck(parsedCommand.commandName, false, "Requires MANUAL mode");
    return;
  }

  desiredMotorSpeeds_.leftMotorSpeed = constrain(parsedCommand.leftMotorSpeed, MIN_MOTOR_SPEED, MAX_MOTOR_SPEED);
  desiredMotorSpeeds_.rightMotorSpeed = constrain(parsedCommand.rightMotorSpeed, MIN_MOTOR_SPEED, MAX_MOTOR_SPEED);
  lastRemoteDriveCommandMs_ = nowMs;
  remoteCommandTimedOut_ = false;
  controlSource_ = "BACKEND_JOYSTICK";

  telemetryPublisher_->publishCommandAck(parsedCommand.commandName, true, "Drive applied");
}

void CarController::handleModeButtonShortPress() {
  if (currentDriveMode_ == DriveMode::EmergencyStop) return;

  const DriveMode previousDriveMode = currentDriveMode_;
  if (currentDriveMode_ == DriveMode::ManualRemote) {
    enterIdleMode("Button: IDLE");
  } else {
    enterManualRemoteMode("Button: MANUAL");
  }
  telemetryPublisher_->publishModeChangedByButton(previousDriveMode, currentDriveMode_);
}

void CarController::handleModeButtonLongPress() {
  engine_->stop();
  if (currentDriveMode_ != DriveMode::EmergencyStop) {
    enterStatusDisplayMode("Long press: Status Display");
  } else {
    lcdDisplay_->turnOn();
  }
}

void CarController::updateManualRemoteMode(unsigned long nowMs) {
  if (lastRemoteDriveCommandMs_ != 0 && nowMs - lastRemoteDriveCommandMs_ > COMMAND_TIMEOUT_MS) {
    desiredMotorSpeeds_ = MotorSpeeds();
    effectiveMotorSpeeds_ = MotorSpeeds();
    engine_->stop();
    if (!remoteCommandTimedOut_) {
      telemetryPublisher_->publishEvent("timeout", "Remote command timeout");
    }
    remoteCommandTimedOut_ = true;
    return;
  }

  effectiveMotorSpeeds_ = desiredMotorSpeeds_;
  if (safetyGuard_->shouldBlockForwardMotion() && motorSpeedsMoveForward(effectiveMotorSpeeds_)) {
    effectiveMotorSpeeds_.leftMotorSpeed = 0;
    effectiveMotorSpeeds_.rightMotorSpeed = 0;
  }
  if (safetyGuard_->shouldBlockBackwardMotion() && motorSpeedsMoveBackward(effectiveMotorSpeeds_)) {
    effectiveMotorSpeeds_.leftMotorSpeed = 0;
    effectiveMotorSpeeds_.rightMotorSpeed = 0;
  }

  engine_->setMotorSpeeds(effectiveMotorSpeeds_.leftMotorSpeed, effectiveMotorSpeeds_.rightMotorSpeed);
}

void CarController::updateSensorsIfDue(unsigned long nowMs) {
  if (nowMs - lastSensorReadMs_ < SENSOR_READ_INTERVAL_MS) return;

  distanceSensorArray_->update(nowMs);
  latestDistanceReadings_ = distanceSensorArray_->getReadings();
  latestSafetyStatus_ = safetyGuard_->update(latestDistanceReadings_, latestCliffReadings_);
  lastSensorReadMs_ = nowMs;
}

void CarController::publishTelemetryIfDue(unsigned long nowMs) {
  if (nowMs - lastTelemetryMs_ < TELEMETRY_INTERVAL_MS) return;
  telemetryPublisher_->publishTelemetry(buildTelemetry(nowMs));
  lastTelemetryMs_ = nowMs;
}

void CarController::updateLocalDisplay(unsigned long nowMs) {
  if (isRunningMode(currentDriveMode_)) {
    lcdDisplay_->turnOff();
    return;
  }
  lcdDisplay_->turnOn();
  lcdDisplay_->updateStatus(currentDriveMode_, batteryMonitor_->getBatteryPercent(),
      batteryMonitor_->getBatteryVoltage(), WiFi.localIP().toString().c_str(),
      latestSafetyStatus_.obstacleDetected, latestSafetyStatus_.cliffDetected,
      personDetectedByAi_, emergencyStopReason_.c_str(), nowMs);
}

void CarController::enterIdleMode(const String& reason) {
  currentDriveMode_ = DriveMode::Idle;
  desiredMotorSpeeds_ = MotorSpeeds();
  effectiveMotorSpeeds_ = MotorSpeeds();
  controlSource_ = "NONE";
  engine_->stop();
  if (reason.length() > 0) telemetryPublisher_->publishEvent("idle", reason);
}

void CarController::enterManualRemoteMode(const String& reason) {
  currentDriveMode_ = DriveMode::ManualRemote;
  desiredMotorSpeeds_ = MotorSpeeds();
  effectiveMotorSpeeds_ = MotorSpeeds();
  lastRemoteDriveCommandMs_ = millis();
  remoteCommandTimedOut_ = false;
  controlSource_ = "BACKEND_JOYSTICK";
  engine_->stop();
  if (reason.length() > 0) telemetryPublisher_->publishEvent("manual", reason);
}

void CarController::enterStatusDisplayMode(const String& reason) {
  currentDriveMode_ = DriveMode::StatusDisplay;
  desiredMotorSpeeds_ = MotorSpeeds();
  effectiveMotorSpeeds_ = MotorSpeeds();
  controlSource_ = "STATUS";
  engine_->stop();
  lcdDisplay_->turnOn();
  if (reason.length() > 0) telemetryPublisher_->publishEvent("status", reason);
}

void CarController::enterEmergencyStop(const String& reason) {
  currentDriveMode_ = DriveMode::EmergencyStop;
  emergencyStopReason_ = reason;
  desiredMotorSpeeds_ = MotorSpeeds();
  effectiveMotorSpeeds_ = MotorSpeeds();
  controlSource_ = "SAFETY";
  engine_->stop();
  telemetryPublisher_->publishEvent("emergency", reason);
}

bool CarController::motorSpeedsMoveForward(const MotorSpeeds& motorSpeeds) const {
  return motorSpeeds.leftMotorSpeed > 0 || motorSpeeds.rightMotorSpeed > 0;
}

bool CarController::motorSpeedsMoveBackward(const MotorSpeeds& motorSpeeds) const {
  return motorSpeeds.leftMotorSpeed < 0 || motorSpeeds.rightMotorSpeed < 0;
}

bool CarController::isRunningMode(DriveMode driveMode) const {
  return driveMode == DriveMode::ManualRemote || driveMode == DriveMode::LearningMap;
}

CarTelemetry CarController::buildTelemetry(unsigned long nowMs) const {
  CarTelemetry carTelemetry;
  carTelemetry.mode = currentDriveMode_;
  carTelemetry.timestampMs = nowMs;
  carTelemetry.leftMotorSpeed = engine_->leftMotorSpeed();
  carTelemetry.rightMotorSpeed = engine_->rightMotorSpeed();
  carTelemetry.leftSpeedValue = leftSpeedSensor_->speedValue();
  carTelemetry.rightSpeedValue = rightSpeedSensor_->speedValue();
  carTelemetry.desiredLeftMotorSpeed = desiredMotorSpeeds_.leftMotorSpeed;
  carTelemetry.desiredRightMotorSpeed = desiredMotorSpeeds_.rightMotorSpeed;
  carTelemetry.effectiveLeftMotorSpeed = effectiveMotorSpeeds_.leftMotorSpeed;
  carTelemetry.effectiveRightMotorSpeed = effectiveMotorSpeeds_.rightMotorSpeed;
  carTelemetry.remoteCommandTimedOut = remoteCommandTimedOut_;
  carTelemetry.distanceCm = latestDistanceReadings_.frontDistanceCm;
  carTelemetry.distanceValid = latestDistanceReadings_.frontValid;
  carTelemetry.distanceReadings = latestDistanceReadings_;
  carTelemetry.cliffReadings = latestCliffReadings_;
  carTelemetry.obstacleDetected = latestSafetyStatus_.obstacleDetected;
  carTelemetry.forwardUnsafe = latestSafetyStatus_.forwardUnsafe;
  carTelemetry.backwardUnsafe = latestSafetyStatus_.backwardUnsafe;
  carTelemetry.cliffDetected = latestSafetyStatus_.cliffDetected;
  carTelemetry.personDetected = personDetectedByAi_;
  carTelemetry.emergencyStopReason = emergencyStopReason_;
  carTelemetry.controlSource = controlSource_;
  carTelemetry.batteryVoltage = 0.0F;
  carTelemetry.batteryPercent = -1;
  carTelemetry.lcdStatus = lcdDisplay_->status();
  carTelemetry.lcdEnabled = lcdDisplay_->isEnabled();
  carTelemetry.currentNode = WiFi.localIP().toString(); // Use IP as node for now
  return carTelemetry;
}

bool CarController::commandAllowedInEmergency(CommandType commandType) const {
  return commandType == CommandType::ResetEmergency || commandType == CommandType::EmergencyStop;
}