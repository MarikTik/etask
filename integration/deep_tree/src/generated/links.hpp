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
#include <cstdint>

namespace generated {

    /**
    * @brief This schema's wire contract, reduced to eight bytes.
    *
    * Two peers built from the same schema agree on every uid, every argument
    * list, every result shape and every link's frame layout. Two peers built
    * from different ones may agree on all of the layout and none of the
    * meaning: the frames parse, the checksum passes, and this device runs the
    * wrong task with plausible-looking arguments. That is what this catches.
    *
    * Exchanged in a fixed handshake preamble at connect - fixed because two
    * peers that disagree about a header cannot use a normal frame to say so.
    * A link whose peer sends a different value refuses task traffic rather
    * than misreading it; the other links keep working.
    *
    * Derived from a canonical rendering of the schema, so reordering the YAML
    * cannot change it and any real contract change must.
    */
    inline constexpr std::uint64_t schema_fingerprint = 0x570C5302C06F6996ULL;

} // namespace generated

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
