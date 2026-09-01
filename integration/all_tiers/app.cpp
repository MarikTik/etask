/**
* @file app.cpp
*
* @brief Your application's startup and per-tick logic.
*
* @note User-owned. This is where the app actually does things. It is a normal
*       translation unit (compiled once), so it is the right home for real logic -
*       unlike the header-only wiring in config/ that it draws on.
*/
#include "app.hpp"
#include "config/wiring.hpp"
#include "support/lifecycle/scenarios.hpp"

#ifdef ARDUINO
#include <Arduino.h>
#endif

namespace app {

    /**
    * @brief Drives the whole conformance run, once.
    *
    * The scenarios own their own ticking - each one calls `update()` exactly as
    * many times as its expectation is written against - so this application
    * deliberately has no free-running loop. A background tick would advance
    * tasks between scenarios and make every count depend on how fast the host
    * got round to the next one.
    */
    void setup() {
    #ifdef ARDUINO
        Serial.begin(115200);
        // The USB-serial bridge enumerates after the sketch starts, so the
        // opening lines of the report would otherwise be written into a port
        // nothing is listening to yet.
        while (not Serial) {}
        delay(2000);
    #endif

        support::lifecycle::run_all();
    }

    /**
    * @brief Nothing. The run finished in `setup()`.
    *
    * Left empty rather than ticking the manager: every task the scenarios
    * started has concluded by the time `run_all()` returns, and a manager driven
    * afterwards could only report on tasks that no longer exist.
    */
    void loop() {
    }

} // namespace app
