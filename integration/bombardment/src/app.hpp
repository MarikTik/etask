/**
* @file app.hpp
*
* @brief The bombardment harness's lifecycle: run every check, then report.
*
* @note User-owned. This is the scaffolded `app::setup`/`app::loop` pair, used
*       for something slightly unusual: the whole test suite runs inside
*       `setup()`, and `loop()` does nothing afterwards.
*
*       That is deliberate, and it is what lets one source tree serve both
*       targets. On the host, `main()` calls `setup()`, reads @ref app::failures,
*       and exits with it. On an ESP32 there is nothing to exit *to* - the
*       Arduino core calls `loop()` forever - so the transcript has to be
*       complete by the time `setup()` returns, and `loop()` only has to avoid
*       disturbing what the checks established. A suite spread across `loop()`
*       calls would have needed a state machine on one target and not the other,
*       and the two would have drifted.
*
* Every check prints its own result, so the transcript is the test report and
* @ref app::failures is only the summary. See verify.py, which parses the
* former and cross-checks the latter.
*/
#ifndef APP_HPP_
#define APP_HPP_

namespace app {

    /**
    * @brief Runs every bombardment check, printing a transcript as it goes.
    *
    * Each check is independent: it starts from an empty manager and drains what
    * it registered before returning, so a failure in one does not cascade into
    * the next and turn one bug into a page of noise.
    */
    void setup();

    /**
    * @brief One idle tick. Nothing is left running by the time this is reached.
    *
    * Still calls `update()` rather than returning immediately: on the ESP32 this
    * is the only thing running after the suite, and a manager that has been
    * driven hard should be shown to keep ticking quietly on an empty task set.
    */
    void loop();

    /**
    * @brief How many checks failed. Zero if the framework behaved as documented.
    *
    * @return The failure count, meaningful only after @ref setup has returned.
    */
    [[nodiscard]] int failures();

} // namespace app

#endif // APP_HPP_
