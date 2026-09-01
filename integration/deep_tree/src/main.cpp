/**
* @file main.cpp
*
* @brief The host entry point: a uid-in, identity-out probe driven by verify.py.
*
* @note User-owned. Only the host (CMake) build compiles this file; the
*       PlatformIO build supplies its own Arduino entry point and drives
*       `app::setup()` / `app::loop()` instead.
*
* ## The protocol, and why there is one
*
* Reads decimal uids from stdin, one per line, and writes one line per uid to
* stdout:
*
* ```
* <requested-uid> <status> <report-count> <reported-uid> <phase>
* ```
*
* The alternative was to compile the list of expected uids into this file and
* have it assert against itself. That would have been a weaker test of exactly
* the wrong thing: the uids come from `.schema.uids.json`, and a check that
* baked them into C++ could only ever confirm that the C++ agreed with itself.
* Driving from stdin keeps the ledger the single source of the numbers, so
* verify.py compares the ledger against the *binary*, and the binary holds no
* opinion about what it should contain.
*
* It also means adding a task to the schema changes nothing here. The ledger
* grows, verify.py asks about one more uid, and this file is untouched - which
* is the property the ledger test in verify.py depends on.
*/
#include "support/exercise.hpp"
#include "support/witness.hpp"
#include <cstdint>
#include <iostream>
#include <string>

int main()
{
    // Unbuffered pairing of the two streams is not wanted here: the driver
    // reads everything after the process exits, and flushing per line over 294
    // lines is pure cost.
    std::ios::sync_with_stdio(false);

    std::string line;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;

        // An unparseable line is reported rather than skipped: silently
        // dropping one would show up in verify.py as a task that never ran,
        // which is a very different diagnosis from a malformed request.
        std::uint16_t uid = 0;
        try {
            uid = static_cast<std::uint16_t>(std::stoul(line));
        } catch (const std::exception&) {
            std::cout << line << " parse-error 0 0 0\n";
            continue;
        }

        const support::result outcome = support::exercise(uid);
        std::cout << uid << ' '
                  << static_cast<unsigned>(outcome.status) << ' '
                  << outcome.reports << ' '
                  << outcome.reported_uid << ' '
                  << static_cast<unsigned>(outcome.reported_phase) << '\n';
    }

    // The witness is sized so that no plausible run fills it, but "plausible"
    // is a claim about the driver, not a guarantee - so say if it was wrong.
    if (support::witness::overflowed) {
        std::cerr << "witness log overflowed; some reports were dropped\n";
        return 1;
    }
    return 0;
}
