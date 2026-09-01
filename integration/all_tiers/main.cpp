/**
* @file main.cpp
*
* @brief Entry point for both targets: forwards whichever one this build has to
*        the same `app::setup()` / `app::loop()`.
*
* @note User-owned, and intentionally trivial. The application logic lives in
*       app.hpp/app.cpp, so this file is only the adapter between a platform's
*       entry point and the app.
*
*       Both forms live here, selected by `ARDUINO`, rather than in two files
*       with one filtered out of each build. This project's whole purpose is
*       that the host and the board run the *same* conformance scenarios, and
*       two entry points that can drift is the one way that could quietly stop
*       being true.
*
*       The plain-`main` form departs from the scaffolded shape in one way:
*       there is no `for(;;)`. The entire run happens inside `app::setup()`, and
*       the host build is a program `verify.py` waits on, so it has to end. On
*       the board the core's own `loop()` still spins, idle, exactly as the
*       scaffold intends.
*/
#include "app.hpp"

#ifdef ARDUINO
#include <Arduino.h>

/// @brief The Arduino core's one-time hook; runs the whole conformance report.
void setup() { app::setup(); }

/// @brief The Arduino core's repeating hook. Idle: the run finished in setup().
void loop()  { app::loop(); }

#else

/**
* @brief Runs the conformance scenarios once and exits.
*
* @return 0 always. Whether the run was *correct* is `verify.py`'s judgement to
*         make from the report, never this program's - a firmware that graded
*         itself could pass by failing to notice.
*/
int main() {
    app::setup();
    return 0;
}

#endif
