#include "camera.h"

void CameraModule::begin() {
  available_ = false;
}

bool CameraModule::isAvailable() const {
  return available_;
}

const char* CameraModule::statusMessage() const {
  return available_ ? "Camera available" : "Camera handled by PC or ESP32-CAM node";
}
