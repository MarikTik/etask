/**
* @file arduino_main.cpp
*
* @brief Arduino-core entry point: the board's equivalent of main.cpp.
*
* @note User-owned. Compiled only by the PlatformIO build (see the
*       `build_src_filter` in platformio.ini, which takes this file and excludes
*       main.cpp). The two are alternatives, not layers: an Arduino core defines
*       `setup`/`loop` as program-level functions and supplies its own `main`,
*       while the host build's `main.cpp` drives the same `app::` functions from
*       a plain `main`.
*
* ## What this build does and does not prove
*
* It proves the half that is compile-time, which for the per-link machinery is
* most of it: that both links' frame sizes, the `carries()` allowlist, the
* fingerprint constant and every `static_assert` binding them together resolve
* identically on Xtensa and on the host. `packet_size_for` rounds to a literal 8
* rather than to `sizeof(std::size_t)` precisely so that a 32-bit target and a
* 64-bit host cannot derive different frame sizes from one schema - and this
* build is what checks that claim rather than trusting it.
*
* It does not prove the runtime half. The descriptors below are placeholders: a
* real deployment opens a UART for `bench` and an lwIP socket for `net` and hands
* those in. Wiring real hardware here would make the file a device driver rather
* than an entry point, and the on-device behaviour is the `hardware` CI job's
* subject, not this one's.
*/
#include <Arduino.h>
#include "app.hpp"

/// @brief Placeholder descriptors, standing in for the board's real ports.
///
/// Negative on purpose: every read and write against them fails immediately and
/// harmlessly, so the firmware links and runs its loop without pretending to
/// have a peer. A real port here would be a lie about what this build tests.
static constexpr int no_port = -1;

/**
* @brief Board bring-up, forwarded to the application.
*
* Runs once, before the first `loop()`.
*/
void setup()
{
    app::bind_links(no_port, no_port);
    app::setup();
}

/**
* @brief One iteration of the run loop, forwarded to the application.
*
* Services both links and advances every running task.
*/
void loop()
{
    app::loop();
}
