/**
* @file witness.cpp
*
* @brief Storage for the witness log declared in witness.hpp.
*
* @note User-owned support code, not generated.
*
* The members are `static` rather than `inline` so the log is one array in one
* translation unit. With 294 task bodies including this header, an `inline`
* definition would be correct but would leave the array's linkage to the
* linker's deduplication - and this project's whole subject is whether 294
* things that were written once are genuinely distinct at the end. Its own
* fixture should not depend on that same folding being right.
*/
#include "support/witness.hpp"

namespace support {

    entry witness::log[witness::capacity]{};
    std::size_t witness::count = 0;
    bool witness::overflowed = false;

} // namespace support
