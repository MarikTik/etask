/**
* @file board_main.cpp
*
* @brief The Arduino entry point, forwarding to the app lifecycle.
*
* @note User-owned, and intentionally trivial. Only the PlatformIO (ESP32) build
*       compiles this file; the host build filters it out and uses `main.cpp`,
*       which speaks the stdin protocol verify.py drives.
*
*       Two entry points rather than one `#ifdef ARDUINO` inside `main.cpp`,
*       because they are not two spellings of the same thing: the host build
*       runs a probe driven from outside and exits, and the board build runs a
*       device that never exits. Folding both into one file would put the
*       project's two quite different purposes behind a preprocessor branch.
*/
#include "app.hpp"

#if defined(ARDUINO)
#include <Arduino.h>

/// @brief Arduino's one-time startup hook.
void setup()
{
    app::setup();
}

/// @brief Arduino's per-iteration hook.
void loop()
{
    app::loop();
}
#endif
