/**
* @file main.cpp
*
* @brief Plain-`main` entry point: drives the application's lifecycle.
*
* @note User-owned, and intentionally trivial. The application logic lives in
*       `app::setup()` / `app::loop()` (see app.hpp), so this file is just the
*       adapter between the host's entry point and the app.
*
*       On the Arduino core this file is not compiled at all - `platformio.ini`
*       filters it out in favour of arduino_main.cpp, which forwards the same two
*       hooks as the sketch-level `setup()`/`loop()`.
*
* ## Why this one returns rather than looping
*
* The scaffolded entry point is `while (true) app::loop();`, which is right for
* firmware and wrong for a test binary: the host driver runs this program,
* reads its transcript, and needs it to *end*. `app::setup()` runs the whole
* suite in one pass (see app.cpp), so by the time it returns there is nothing
* left to do and the exit status is the honest answer to "did it get through".
*
* A handful of loop() iterations run first anyway. They should do nothing - the
* harness ticked every case to completion already - and that is the point: if a
* task were somehow left live, it would be completed here, and its stray reply
* would appear in the transcript after `done` where the driver will notice it.
*/
#include "app.hpp"

/// @brief How many idle iterations run before the process exits.
///
/// Small and fixed. Enough that a task wrongly left running would be advanced
/// and show itself, few enough that a genuinely hung task cannot make the test
/// hang with it.
static constexpr int trailing_iterations = 8;

int main() {
    app::setup();
    for (int i = 0; i < trailing_iterations; ++i)
        app::loop();
    return 0;
}
