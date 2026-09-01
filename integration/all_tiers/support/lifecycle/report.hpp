/**
* @file report.hpp
*
* @brief One line of observation, out to wherever this build can be watched.
*
* @note User-owned. The generator never writes here.
*
* The scenarios have to say what happened on two targets with nothing in common
* at the output end: a host process writing to stdout, and an ESP32 writing to a
* UART through the Arduino core. This is the one place that difference lives, so
* nothing else in the project has to know which target it is on.
*
* Values are printed as unsigned decimals throughout. Every field this project
* reports - a status code, a hook mask, a count, a completion reason - is a
* single byte, and the host reads them all the same way, so there is nothing to
* gain from a second format and something to lose in a parser that has to guess.
*/
#ifndef SUPPORT_LIFECYCLE_REPORT_HPP_
#define SUPPORT_LIFECYCLE_REPORT_HPP_
#include <cstdint>

#ifdef ARDUINO
#include <Arduino.h>
#else
#include <cstdio>
#endif

namespace support::lifecycle {

    /**
    * @class report
    *
    * @brief Emits the `etask <key>=<value>` lines the host parses.
    *
    * A class of static members rather than free functions: it keeps the two
    * target-specific bodies adjacent to each other and to the format they share,
    * which is the thing that must not drift between them.
    */
    class report {
    public:
        /**
        * @brief Prints one observation.
        *
        * @param key   Dotted name of what is being reported, e.g.
        *        `"stateful.pauses"`. Must be a literal or otherwise outlive the
        *        call; it is printed, not stored.
        * @param value The observation. Widened from the byte-sized fields the
        *        scenarios actually deal in so that a count and a size can share
        *        one function.
        */
        static void value(const char* key, unsigned long value_in)
        {
        #ifdef ARDUINO
            Serial.print("etask ");
            Serial.print(key);
            Serial.print('=');
            Serial.println(value_in);
        #else
            std::printf("etask %s=%lu\n", key, value_in);
        #endif
        }

        /**
        * @brief Marks the end of the run, so the host knows the report is whole.
        *
        * Without it a firmware that crashed halfway would be indistinguishable
        * from one that simply had less to say, and the host would assert against
        * a truncated report - passing on the checks that happened to have been
        * printed already.
        */
        static void done()
        {
        #ifdef ARDUINO
            Serial.println("etask done");
            Serial.flush();
        #else
            std::printf("etask done\n");
            std::fflush(stdout);
        #endif
        }
    };

} // namespace support::lifecycle

#endif // SUPPORT_LIFECYCLE_REPORT_HPP_
