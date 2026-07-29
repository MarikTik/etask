// SPDX-License-Identifier: MIT
/**
* @file smoke.cpp
*
* @brief Minimal translation unit including every etask/core header.
*
* Exists so `ETASK_BUILD_EXAMPLES` produces at least one compiled target that
* includes `etask/core/core.hpp`. Without this, `etask` (an INTERFACE-only
* library) never appears in `compile_commands.json`, and IDE IntelliSense has
* no compile flags to resolve the FetchContent-fetched `ecomm`/`etools`
* include paths against when browsing `etask/core` headers directly.
*/
#include <etask/core/core.hpp>

int main() {
    return 0;
}
