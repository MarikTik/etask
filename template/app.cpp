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
// #include "config/router.hpp"   // uncomment once you enable external comms (see wiring.hpp)

namespace app {

    void setup() {
        // TODO: initialize hardware and transports.
        //
        // Start any always-on tasks here, e.g.:
        //   (void)config::internal.register_task(global::task_id::blink);
    }

    void loop() {
        // config::poll_inbound();     // uncomment with a router to service arriving packets
        config::manager.update();      // advance tasks, deliver results
    }

} // namespace app
