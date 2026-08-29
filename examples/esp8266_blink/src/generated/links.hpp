/**
* @file links.hpp
*
* @brief The packet types for this system's external links.
*
* This system declares no `links:`, so it speaks over the internal channel only - which
* is what the great majority of projects do. The file is generated anyway, and empty of
* packet types by design: a config header can include it and branch on `any` without
* having to know whether the schema declared a link.
*
* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema
*          on every generate; hand edits are overwritten. Regenerate via the
*          CMake `etask-generate` target, or `etask generate`.
*/
#ifndef GENERATED_LINKS_HPP_
#define GENERATED_LINKS_HPP_
#include <cstddef>

namespace generated::links {

    /**
    * @brief Whether this system declares any external link.
    *
    * It does not, so nothing else is generated here - the system speaks over the
    * internal channel only. Emitted either way so a config header can include this file
    * unconditionally and branch on the constant instead of on the shape of the schema.
    */
    inline constexpr bool any = false;

} // namespace generated::links
#endif // GENERATED_LINKS_HPP_
