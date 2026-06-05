#pragma once
#include "app_config.h"

namespace ConfigPortal {
  // Start AP + web server and block until config is saved.
  // After save, ESP8266 reboots automatically.
  void start();
}