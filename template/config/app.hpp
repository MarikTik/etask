// SPDX-License-Identifier: MIT
/**
* @file app.hpp
*
* @brief The application's two lifecycle entry points: `setup` and `loop`.
*
* @note User-owned config. The application owns its lifecycle here, decoupled
*       from any particular `main`. This is deliberate: Arduino cores define
*       `setup()`/`loop()` as program-level functions, but bare-metal and RTOS
*       vendors use a plain `main()`. Exposing them as ordinary `config::`
*       functions lets *any* entry point drive the app the same way:
*
*       - plain main (see main.cpp):
*         ```cpp
*         int main() { config::setup(); for (;;) config::loop(); }
*         ```
*       - an Arduino sketch:
*         ```cpp
*         void setup() { config::setup(); }
*         void loop()  { config::loop(); }
*         ```
*
* Put your actual startup and per-tick logic in app.cpp.
*/
#ifndef CONFIG_APP_HPP_
#define CONFIG_APP_HPP_

namespace config {

    /**
    * @brief One-time initialization. Runs once before the first `loop()`.
    *
    * Bring up hardware and transports, and start any always-on tasks (e.g.
    * `config::internal.register_task(global::task_id::...)`).
    */
    void setup();

    /**
    * @brief One iteration of the run loop. Call repeatedly (forever).
    *
    * Advances every running task one step (`config::manager.update()`), and -
    * when external comms are enabled - routes any arriving packets first.
    */
    void loop();

} // namespace config

#endif // CONFIG_APP_HPP_
