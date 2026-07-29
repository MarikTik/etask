// SPDX-License-Identifier: MIT
/**
* @file main.cpp
*
* @brief Plain-`main` entry point: drives the application's lifecycle.
*
* @note User-owned, and intentionally trivial. The application logic lives in
*       `config::setup()` / `config::loop()` (see config/app.hpp), so this file
*       is just the adapter between your platform's entry point and the app.
*
*       On an Arduino core you would not use this file at all - instead the
*       sketch forwards the program-level hooks:
*       ```cpp
*       void setup() { config::setup(); }
*       void loop()  { config::loop(); }
*       ```
*/
#include "config/app.hpp"

int main() {
    config::setup();
    while (true) config::loop();
    return 0;
}
