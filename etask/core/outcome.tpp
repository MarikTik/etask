// SPDX-License-Identifier: MIT
/**
* @file outcome.tpp
*
* @brief Definition of outcome.hpp api.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-10
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_OUTCOME_TPP_
#define ETASK_CORE_OUTCOME_TPP_
#include "outcome.hpp"

namespace etask::core {

    template<typename... Ts,
             std::enable_if_t<!(sizeof...(Ts) == 1 &&
                 std::conjunction_v<std::is_same<std::decay_t<Ts>, outcome>...>), int>>
    outcome::outcome(const Ts&... values) noexcept
    {
        const detail::result_region region = detail::current_result_region;
        // Values with no bound region == constructed outside on_complete: a
        // programming error. Flag it in debug; stay a no-op in release.
        assert((sizeof...(Ts) == 0 || region.data != nullptr) &&
               "etask::core::outcome must be constructed by returning from on_complete");
        if (region.data == nullptr)
            return;
        if constexpr (sizeof...(Ts) > 0) {
            // The flat format is fixed-layout, so the exact wire size of the
            // result is known at compile time; only the region's capacity is
            // a runtime value. `buffer::pack` is all-or-nothing, so an
            // over-large result would otherwise land as a silent empty one.
            constexpr std::size_t needed = eser::flat::serialized_size_of<Ts...>();
            // The discard region is exempt: a channel with nowhere to put the
            // result binds zero capacity on purpose, so "it does not fit" is the
            // expected answer there and not a schema or packet-sizing mistake.
            // `result_too_large` is still reported - the caller is told the bytes
            // went nowhere - but a debug build must not abort on the one case
            // that is working as designed.
            assert((needed <= region.capacity ||
                    region.data == &detail::discard_region_anchor) &&
                   "etask::core::outcome: result does not fit the packet's result region");
            if (needed > region.capacity) {
                _status = status_code::result_too_large;
                return;
            }
        }
        _buffer = etools::memory::buffer<noop_deleter>{
            std::unique_ptr<std::byte[], noop_deleter>{region.data, noop_deleter{}},
            region.capacity
        };
        _buffer.pack(values...);
    }

    inline outcome&& outcome::with_status(status_code code) && noexcept
    {
        assert(!is_manager_status(code) &&
               "etask::core::outcome::with_status: manager/API codes are not a task's to report");
        _status = code;
        return std::move(*this);
    }

    inline status_code outcome::status() const noexcept
    {
        return _status;
    }

    inline std::size_t outcome::size() const noexcept
    {
        return _buffer.size();
    }

} // namespace etask::core

#endif // ETASK_CORE_OUTCOME_TPP_
