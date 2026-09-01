/**
* @file main.cpp
*
* @brief Entry point for both of this project's targets: a plain `main()` on the
*        host and the Arduino core's `setup`/`loop` on the ESP32.
*
* @note User-owned. The scaffold ships a plain-`main` version of this file and
*       tells you to write the Arduino sketch separately; this project cannot,
*       because the *same tree* has to build both ways. Two entry-point files
*       would work, but they would be two files to keep in step for a project
*       whose entire subject is two builds agreeing - so the fork is made here,
*       once, on the one thing that actually differs.
*
*       Both branches do the same thing. The application lives in
*       `app::setup()` / `app::loop()` (see app.hpp) precisely so that the
*       entry point can be this thin.
*/
#include "app.hpp"

#ifdef ARDUINO

// The core owns the loop: it calls setup() once, then loop() forever.
void setup() { app::setup(); }
void loop()  { app::loop(); }

#else

/**
* @brief Host entry point: runs the same lifecycle the Arduino core would.
*
* @return Never returns; the signature is `main`'s.
*/
int main()
{
    app::setup();
    for (;;) app::loop();
}

#endif // ARDUINO
