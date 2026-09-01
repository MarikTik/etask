/**
* @file main.cpp
*
* @brief Arduino entry point: forwards the core's setup/loop to the app.
*
* @note User-owned, and intentionally trivial. The Arduino core defines `main`
*       itself and calls the program-level `setup()`/`loop()` below, so this file
*       is only the adapter between it and `app::`.
*
*       The host build compiles src/host_main.cpp instead, and never this file -
*       see platformio.ini's `build_src_filter` for the other half of that split.
*
*       There is nothing to report on a board: the harness has no exit status to
*       return to and no test runner reading it, so `app::failures()` goes
*       unread here. The transcript on the serial monitor is the result, which
*       is why every check prints its own verdict rather than only counting.
*/
#include <Arduino.h>

#include "app.hpp"

/**
* @brief Brings up the serial link, then runs the whole bombardment suite.
*
* The delay is not superstition: an ESP32 finishes booting well before a host's
* USB serial adapter has enumerated, and the suite prints its entire transcript
* within a few milliseconds of `app::setup()` starting. Without a pause the
* interesting output is gone before anything is listening, and the board looks
* like it silently did nothing.
*/
void setup()
{
    Serial.begin(115200);
    delay(2000);
    app::setup();
}

/// @brief One idle tick. See `app::loop` - nothing is left running by now.
void loop()
{
    app::loop();
}
