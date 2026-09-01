/**
* @file app.cpp
*
* @brief This project's startup and per-tick logic.
*
* @note User-owned. This is where the app actually does things. It is a normal
*       translation unit (compiled once), so it is the right home for real logic -
*       unlike the header-only wiring in config/ that it draws on.
*
* `many_returns` is a test project, so "what the app does" is: run every case in
* the reply-direction suite once, print the frames, and then idle. That shape
* holds on both targets. On the host the driver reads the transcript off stdout
* and the process exits; on a board the same transcript goes to the serial
* console, where the same driver can read it back over the port.
*/
#include "app.hpp"
#include "config/wiring.hpp"
#include "support/harness.hpp"

namespace app {

    void setup() {
        // The whole suite runs here rather than being spread across loop()
        // iterations. Every case is deterministic and self-contained - deliver a
        // request, tick until it has answered, print - so there is nothing for a
        // scheduler to interleave, and a single pass with a definite end is what
        // lets the driver tell a completed run from a hung one.
        support::harness::run();
    }

    void loop() {
        // Nothing left to advance: the harness ticked each of its cases to
        // completion before printing it. The manager is still updated so that a
        // task somehow left running would keep being polled rather than silently
        // stalling - a difference worth preserving even though nothing here
        // should reach it.
        config::manager.update();
    }

} // namespace app
