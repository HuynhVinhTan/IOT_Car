#pragma once

#include "app_config.h"

// ---------------------------------------------------------------------------
// Config Portal – Captive AP + WebServer for provisioning
// ---------------------------------------------------------------------------

/// Start the config portal in blocking mode.
/// Creates a WiFi AP named `apSsid`, starts a web server on port 80,
/// and blocks until the user submits valid config (then saves & restarts).
void startConfigPortal(const char *apSsid = "SmartCar-Setup");