/**
* @file main.cpp
*
* @brief Plain-`main` entry point: drives the application's lifecycle.
*
* @note User-owned, and intentionally trivial. The application logic lives in
*       `app::setup()` / `app::loop()` (see app.hpp), so this file is just the
*       adapter between your platform's entry point and the app.
*
*       On an Arduino core you would not use this file at all - instead the
*       sketch forwards the program-level hooks:
*       ```cpp
*       void setup() { app::setup(); }
*       void loop()  { app::loop(); }
*       ```
*
* This host entry point takes the two links' descriptors as arguments because
* the host build exists to be driven by `verify.py`, which owns the other end of
* both. The firmware build takes this file's place with a sketch that opens a
* UART and a socket instead; the app itself does not know the difference, which
* is what lets the host run stand as evidence about the board.
*
*     ./app <bench_fd> <net_fd>
*/
#include "app.hpp"
#include <cstdlib>
#include <cstdio>

int main(int argc, char** argv) {
    if (argc != 3) {
        // A usage error rather than a default, because defaulting to some
        // descriptor would produce a process that runs, answers nothing, and has
        // to be diagnosed - while the harness always has both numbers to hand.
        std::fprintf(stderr, "usage: %s <bench_fd> <net_fd>\n", argv[0]);
        return 2;
    }

    app::bind_links(std::atoi(argv[1]), std::atoi(argv[2]));
    app::setup();
    while (true) app::loop();
    return 0;
}
