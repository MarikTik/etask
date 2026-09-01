/**
* @file scenarios.hpp
*
* @brief The conformance run: every tier and directive exercised in sequence,
*        each observation printed as one line for the host to assert on.
*
* @note User-owned. The generator never writes here.
*
* ## Why the device prints rather than the host inspects
*
* The same binary has to run in two places - a host process under CMake and an
* ESP32 under PlatformIO - and only one of them can be poked at by a debugger.
* A line of text over stdout is also a line of text over serial, so the device
* reports and `verify.py` judges, identically in both. That split is deliberate:
* the firmware states *what happened*, never whether it was correct, so an
* expectation can never be quietly satisfied by the code that produced it.
*
* ## The report format
*
* One `key=value` pair per line, prefixed to keep it separable from any other
* serial chatter a board might emit:
*
* ```
* etask oneshot.status=32 oneshot.hooks=35 oneshot.executions=1
* ```
*
* Flat and positional-free on purpose: a host-side parser that reads a dict of
* names cannot silently mis-align the way an ordered tuple can when a field is
* added, and the assertions in `verify.py` name what they read.
*/
#ifndef SUPPORT_LIFECYCLE_SCENARIOS_HPP_
#define SUPPORT_LIFECYCLE_SCENARIOS_HPP_

namespace support::lifecycle {

    /**
    * @brief Runs every scenario once, in order, reporting as it goes.
    *
    * Ordered rather than independent: each scenario leaves the manager empty
    * before the next begins, so a trace can be read against a known-quiet
    * system. Concurrency is a different project's axis (`bombardment`), and
    * mixing it in here would let a budget rejection masquerade as a lifecycle
    * fault.
    *
    * Runs to completion and returns; nothing here loops forever, so the host
    * binary exits on its own and a board's report ends rather than repeating.
    */
    void run_all();

} // namespace support::lifecycle

#endif // SUPPORT_LIFECYCLE_SCENARIOS_HPP_
