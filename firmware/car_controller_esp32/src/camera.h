#pragma once

#include <Arduino.h>

class CameraModule {
 public:
  void begin();
  bool isAvailable() const;
  const char* statusMessage() const;

 private:
  bool available_ = false;
};
