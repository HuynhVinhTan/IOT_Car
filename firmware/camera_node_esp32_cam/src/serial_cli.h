#pragma once

#include "app_config.h"

// ---------------------------------------------------------------------------
// Serial CLI – only compiled when ENABLE_SERIAL_CLI=1
// ---------------------------------------------------------------------------
#if defined(ENABLE_SERIAL_CLI) && ENABLE_SERIAL_CLI == 1

/// Call once in setup() after Serial.begin().
void serialCliBegin(AppConfig &config);

/// Call in loop() to process any incoming Serial commands.
void serialCliTick(AppConfig &config);

#else
// No-op stubs so main.cpp compiles cleanly in production builds
inline void serialCliBegin(AppConfig &) {}
inline void serialCliTick(AppConfig &) {}
#endif