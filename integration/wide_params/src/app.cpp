/**
* @file app.cpp
*
* @brief This node's startup and per-tick logic: bring up the link, then let the
*        manager answer whatever the host asks.
*
* @note User-owned. Every task in this project is a pure function of its
*       arguments - no hardware is read, nothing is timed, nothing is stored
*       between calls - so there is deliberately almost nothing here. That is
*       the design: anything this file did would be a second explanation for a
*       mismatch the driver reports, and the project exists to have exactly one.
*/
#include "app.hpp"
#include "config/wiring.hpp"

#ifdef ARDUINO
#include <Arduino.h>
#endif

namespace app {

    namespace {

        /// @brief Bits per second on the link to the host. Matches verify.py's
        ///        `--baud` default; the two are one setting in two places, and a
        ///        mismatch shows up as a checksum failure rather than as silence.
        constexpr unsigned long link_baud = 115200;

    } // namespace

    void setup()
    {
#ifdef ARDUINO
        // The only hardware this project touches. Everything past this point is
        // the codec.
        Serial.begin(link_baud);
#else
        // Nothing to bring up. The host build has no link: see the note in
        // config/wiring.hpp about why external comms are not wired here, and
        // what the host build is therefore proving.
        (void)link_baud;
#endif
    }

    void loop()
    {
        // config::poll_inbound();     // enable with the external channel; see wiring.hpp
        config::manager.update();      // advance tasks, deliver results
    }

} // namespace app
