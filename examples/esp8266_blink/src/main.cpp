/**
* @file main.cpp
*
* @brief Arduino entry point: forwards the core's setup/loop to the app.
*
* @note User-owned, and intentionally trivial. The application lives in
*       `app::setup()` / `app::loop()` (see app.hpp), so this file is only the
*       adapter between the Arduino core's entry points and the app - which is
*       why the same app builds under a plain `main()` on another target.
*/
#include <Arduino.h>

#include "app.hpp"

void setup() { app::setup(); }
void loop()  { app::loop(); }
