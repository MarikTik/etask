// SPDX-License-Identifier: MIT
/**
* @file result_region.hpp
*
* @brief The framework-designated destination for a completing task's result.
*
* @ingroup etask_core etask::core
*
* When a task completes, its `on_complete` returns an @ref etask::core::outcome
* built from `return {r1, r2, ...}`. That `outcome` must serialize straight into
* the exact bytes about to go on the wire (or a discard scratch for an internal
* task) - with no heap and no copy. But `on_complete` is a user-overridable
* virtual whose only inputs are the values; it cannot be handed the destination
* as an argument without exposing a raw pointer an override could misuse.
*
* So the destination is supplied out-of-band: the channel installs the current
* result region here, scoped around the single `on_complete` call, and the
* `outcome` constructor reads it. This is safe because the manager completes one
* task at a time; the RAII @ref result_region_scope additionally saves and
* restores the previous region, so even a (non-expected) nested completion is
* correct. A plain `static` - not `thread_local` - is deliberate: elib is
* single-threaded (eser, the serialization backbone, is itself not thread-safe),
* so guarding against concurrent completions would protect against a threat that
* does not exist.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_DETAIL_RESULT_REGION_HPP_
#define ETASK_CORE_DETAIL_RESULT_REGION_HPP_
#include <cstddef>

namespace etask::core::detail {

    /**
    * @brief A writable byte region a completing task packs its result into.
    *
    * @c data is the first result byte (the packet payload past the uid+code
    * header, or an internal scratch); @c capacity is how many bytes are available.
    * A default (null) region means "no completion in progress" - packing into it
    * is a no-op (see @ref etask::core::outcome).
    */
    struct result_region {
        std::byte* data = nullptr;
        std::size_t capacity = 0;
    };

    /// @brief The region the next-constructed @ref etask::core::outcome writes into.
    inline result_region current_result_region{};

    /**
    * @brief Scoped override of @ref current_result_region.
    *
    * Installs @p data / @p capacity as the current region for the lifetime of the
    * scope, restoring whatever was there before on destruction. A channel wraps
    * its one `t.on_complete(reason)` call in this guard.
    */
    struct result_region_scope {
        result_region previous;

        result_region_scope(std::byte* data, std::size_t capacity) noexcept
            : previous{current_result_region}
        {
            current_result_region = result_region{data, capacity};
        }

        ~result_region_scope() noexcept { current_result_region = previous; }

        result_region_scope(const result_region_scope&) = delete;
        result_region_scope& operator=(const result_region_scope&) = delete;
    };

} // namespace etask::core::detail

#endif // ETASK_CORE_DETAIL_RESULT_REGION_HPP_
