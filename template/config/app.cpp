// SPDX-License-Identifier: MIT
/**
* @file app.cpp
*
* @brief Your application's startup and per-tick logic.
*
* @note User-owned config. This is where the app actually does things. It is a
*       normal translation unit (compiled once), so it is the right home for
*       real logic - unlike the header-only wiring it draws on.
*/
#include "app.hpp"
#include "wiring.hpp"
// #include "router.hpp"   // uncomment once you enable external comms (see wiring.hpp)

namespace config {

    void setup() {
        // TODO: initialize hardware and transports.
        //
        // Start any always-on tasks here, e.g.:
        //   (void)internal.register_task(global::task_id::blink);
    }

    void loop() {
        // poll_inbound();     // uncomment with a router to service arriving packets
        manager.update();      // advance tasks, deliver results
    }

} // namespace config
