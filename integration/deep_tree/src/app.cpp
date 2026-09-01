/**
* @file app.cpp
*
* @brief The board-side lifecycle: exercises the tree and reports over Serial.
*
* @note User-owned. This is the entry the PlatformIO (ESP32) build drives. The
*       host build does not compile it - `main.cpp` there speaks the stdin
*       protocol verify.py drives instead.
*
* ## What the board proves that the host cannot
*
* The host build answers whether the *uids* are distinct and whether the ledger
* holds them still. Neither of those needs a board. What needs a board is the
* question of whether a tree this size is a thing an embedded target can
* actually carry: 294 tasks across three managers, 73 nested contexts in one
* composition root, and a two-byte uid space are all cheap on a workstation and
* are not obviously cheap on an MCU.
*
* So this build exists mainly to be *linked* - it is a size and a fit check.
* Beyond that it walks the tree once at startup so that the same identity
* property the host asserts can be eyeballed on the serial console, and then
* idles.
*/
#include "app.hpp"
#include "support/exercise.hpp"
#include "config/wiring.hpp"
#include "generated/task_id.hpp"

#if defined(ARDUINO)
#include <Arduino.h>
#endif

namespace app {

    namespace {

        /**
        * @brief A representative slice of the tree, named rather than enumerated.
        *
        * Not all 294: printing them all over a serial console at boot is noise,
        * and the exhaustive check is the host's job, where the ledger can supply
        * the full list. What is here is one task from each corner the tree has -
        * the deepest scope's four tiers, an abstract sibling that must differ
        * from them, both halves of the flattened-name near miss, the two pinned
        * uids, and the root-level task.
        *
        * Named as `global::task_id` and then narrowed on use, because these are
        * a fixed sample rather than input: there is no wire here to take them
        * from, and spelling them as bare numbers would only invite them to drift
        * from the schema.
        */
        constexpr global::task_id sample[] = {
            global::task_id::mesh_s0_n0_p0_sample,
            global::task_id::mesh_s0_n0_p0_arm,
            global::task_id::mesh_s0_n0_p0_hold,
            global::task_id::mesh_s0_n0_p0_quench,
            // The sibling instance: same definition, and it must not answer with
            // the uid above.
            global::task_id::mesh_s0_n0_p1_sample,
            // The far corner of the fan-out, so a partly-expanded tree shows up.
            global::task_id::mesh_s5_n3_p2_sample,
            // The flattened-name near miss, both halves.
            global::task_id::bus_link_state_probe,
            global::task_id::bus_link_state_probe2,
            // Pinned high and pinned low, in a two-byte tree.
            global::task_id::bus_reserve_emergency_halt,
            global::task_id::bus_reserve_diagnostic,
            // Root-level: no scope path at all.
            global::task_id::census,
        };

        /**
        * @brief Writes one line for one exercised uid, if there is a console.
        *
        * @param requested The uid asked for.
        * @param produced What running it reported.
        */
        void report([[maybe_unused]] std::uint16_t requested,
                    [[maybe_unused]] const support::result& produced)
        {
#if defined(ARDUINO)
            Serial.print(requested);
            Serial.print(' ');
            Serial.print(produced.status);
            Serial.print(' ');
            Serial.print(produced.reports);
            Serial.print(' ');
            Serial.print(produced.reported_uid);
            Serial.print(' ');
            Serial.println(produced.reported_phase);
#endif
        }

    } // namespace

    void setup()
    {
#if defined(ARDUINO)
        Serial.begin(115200);
        // The console is not up the instant begin() returns, and the whole
        // output of this build is one burst at boot - losing its front to an
        // unready UART would make the run look like a failure.
        delay(200);
        Serial.println(F("deep_tree: uid requested/status/reports/reported/phase"));
#endif
        for (const global::task_id id : sample) {
            const auto raw = static_cast<std::uint16_t>(id);
            report(raw, support::exercise(raw));
        }
    }

    void loop()
    {
        // Nothing here starts work, so this only drains whatever `setup()` left
        // live - which, every task in this tree concluding on its first tick,
        // is nothing. It is kept because a task manager that is never updated is
        // not a task manager, and a later addition to this project should find
        // the tick already in place.
        config::manager.update();
    }

} // namespace app
