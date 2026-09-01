/**
* @file host_main.cpp
*
* @brief Host entry point: run the checks once, exit with the failure count.
*
* @note User-owned. Unlike the scaffolded `main` this started from, it does not
*       loop forever - the harness's whole suite runs inside `app::setup()`, and
*       a test binary that never returns cannot be a test.
*
*       Named `host_main.cpp` rather than `main.cpp` because the ESP32 build must
*       not compile it: the Arduino core defines its own `main`, and two would
*       collide at link. `src/main.cpp` is the Arduino forwarder, and
*       platformio.ini's `build_src_filter` excludes this file. That the two
*       entry points can differ so completely while the suite itself does not is
*       exactly why the lifecycle lives in `app::` rather than in either of them.
*/
#include "app.hpp"

/**
* @brief Runs the bombardment suite.
*
* @return 0 if every check passed, otherwise the number that failed - so a
*         caller that only looks at the exit status still learns how bad it is,
*         and CI fails without having to parse the transcript.
*/
int main()
{
    app::setup();
    return app::failures();
}
