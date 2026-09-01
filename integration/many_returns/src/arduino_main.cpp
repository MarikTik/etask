/**
* @file arduino_main.cpp
*
* @brief Arduino-core entry point: forwards the framework's hooks to `app::`.
*
* @note User-owned. The counterpart to main.cpp, and the only file that differs
*       between the two targets - `platformio.ini` compiles this one and filters
*       main.cpp out, while the CMake host build does the reverse.
*
* The Arduino core owns `main()` itself and calls program-level `setup()` and
* `loop()`, so a board build cannot use main.cpp's `int main()`. Everything above
* this line is identical on both targets, which is the property worth having: the
* suite that runs on the host is the same code, the same tasks and the same
* channel as the one that runs on the board.
*
* ## The serial line
*
* `harness::run()` writes with `printf`. On the ESP32 Arduino core stdout is
* wired to `Serial` (UART0), so the transcript reaches the same console the host
* driver reads - and reaches it in the same format, so the driver does not need
* a second parser for the board. The baud rate is set here rather than left to
* the core's default because the default differs between core versions, and a
* driver that guessed wrong would see the transcript as line noise.
*/
#include <Arduino.h>

#include "app.hpp"

/// @brief Console speed, matching `monitor_speed` in platformio.ini.
///
/// The two must agree; they are stated in both places because neither the sketch
/// nor the ini can read the other.
static constexpr unsigned long console_baud = 115200;

void setup() {
    Serial.begin(console_baud);
    // The first bytes out of a just-reset ESP32 are the bootloader's, at a
    // different rate, and a host that opened the port late can miss the start of
    // the transcript entirely. A short settle before the suite runs costs
    // nothing here - this is a test binary that runs once - and makes the
    // transcript reliably complete.
    delay(500);
    app::setup();
}

void loop() {
    app::loop();
}
