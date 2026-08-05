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
*/
#include "app.hpp"

int main() {
    app::setup();
    while (true) app::loop();
    return 0;
}
