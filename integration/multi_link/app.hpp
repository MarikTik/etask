/**
* @file app.hpp
*
* @brief The application's two lifecycle entry points: `setup` and `loop`.
*
* @note User-owned, and the top of the project. `app` is where all the parts are
*       actually acted upon - it draws on `config::` (the wiring and settings) to
*       bring the node to life. It lives at the project root, next to main.cpp,
*       precisely because it is not configuration: it is the running application.
*
*       The lifecycle is decoupled from any particular `main`. Arduino cores
*       define `setup()`/`loop()` as program-level functions, but bare-metal and
*       RTOS vendors use a plain `main()`. Exposing them as ordinary `app::`
*       functions lets *any* entry point drive the app the same way:
*
*       - plain main (see main.cpp):
*         ```cpp
*         int main() { app::setup(); for (;;) app::loop(); }
*         ```
*       - an Arduino sketch:
*         ```cpp
*         void setup() { app::setup(); }
*         void loop()  { app::loop(); }
*         ```
*
* Put your actual startup and per-tick logic in app.cpp.
*/
#ifndef APP_HPP_
#define APP_HPP_

namespace app {

    /**
    * @brief One-time initialization. Runs once before the first `loop()`.
    *
    * Bring up hardware and transports, and start any always-on tasks (e.g.
    * `config::internal.register_task(global::task_id::...)`).
    */
    void setup();

    /**
    * @brief Points the two links at the descriptors they will speak over.
    *
    * Split out of @ref setup because where a link's bytes come from is the one
    * thing that genuinely differs between the board and the host test: on an
    * ESP32 these are a UART and a socket the firmware opens itself, while under
    * `verify.py` they are inherited descriptors the harness already holds the
    * other ends of. Everything after this point - the handshake, the frame
    * sizes, the `carries()` allowlist - is identical in both cases, which is
    * what makes the host run evidence about the board.
    *
    * Call before @ref setup, which opens the handshake on both links and so
    * needs somewhere to send it.
    *
    * @param bench_fd Descriptor for the `bench` link (uart, crc16, reliable).
    * @param net_fd Descriptor for the `net` link (tcp, no checksum of our own).
    */
    void bind_links(int bench_fd, int net_fd);

    /**
    * @brief One iteration of the run loop. Call repeatedly (forever).
    *
    * Advances every running task one step (`config::manager.update()`), and -
    * when external comms are enabled - routes any arriving packets first.
    */
    void loop();

} // namespace app

#endif // APP_HPP_
