// SPDX-License-Identifier: MIT
/**
* @file outcome.hpp
*
* @brief The return type of `task::on_complete`: a task's result, serialized
*        straight into the outgoing packet.
*
* @ingroup etask_core etask::core
*
* A task reports its result by simply returning its values:
* ```cpp
* etask::core::outcome on_complete(etask::core::completion_reason) override {
*     return {ax, ay, az};   // packed directly into the wire packet's payload
* }
* ```
* `outcome`'s variadic constructor serializes those values (via
* `etools::memory::buffer::pack`, i.e. `eser::flat::serialize`) into the region
* the framework designated for this completion - the exact bytes about to be sent
* (@ref etask::core::detail::result_region). There is no heap allocation and no
* intermediate copy.
*
* Only the *return type* carries this behavior; `on_complete` takes no writable
* buffer argument. That is deliberate: `on_complete` is a user-overridable
* virtual, and `outcome` exposes no raw pointer and no unbounded write - the user
* can only return values. `buffer::pack` is all-or-nothing and never overflows,
* so an over-large result is dropped rather than corrupting memory.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_OUTCOME_HPP_
#define ETASK_CORE_OUTCOME_HPP_
#include <cstddef>
#include <cassert>
#include <memory>
#include <type_traits>
#include <etools/memory/buffer.hpp>
#include "detail/result_region.hpp"

namespace etask::core {

    /**
    * @class outcome
    *
    * @brief A task's result, packed in place into the framework-designated region.
    *
    * Construct it by returning the task's result values from `on_complete`
    * (`return {r1, r2, ...}`, `return v`, or `return {}` for no result). The
    * bytes land in @ref detail::current_result_region; nothing is owned or copied.
    */
    class outcome {
        /// @brief Deleter that frees nothing - the bytes belong to the packet, not to us.
        struct noop_deleter {
            void operator()(std::byte*) const noexcept {}
        };

        /// @brief Non-owning view over the designated region; carries the packed size.
        etools::memory::buffer<noop_deleter> _buffer{};

    public:
        /// @brief An empty result (`return {}`), e.g. a task with no return values.
        outcome() noexcept = default;

        /**
        * @brief Packs the task's result values into the current result region.
        *
        * @tparam Ts Types of the returned values (heterogeneous; order is the
        *         wire contract, matching the peer's `unpack<Ts...>()`).
        * @param values The task's result, as written in `return {values...}`.
        *
        * @warning Build an `outcome` **only** by returning from `on_complete`
        *       (`return {v...}`). A region is bound only for the duration of that
        *       call, so an `outcome` with values constructed anywhere else - e.g.
        *       cached in `on_execute` for later return - packs nothing and silently
        *       yields an empty result. In debug builds that misuse trips an assert;
        *       in release it is a harmless no-op (an empty result). A zero-argument
        *       `outcome{}` is always fine.
        * @note The single-argument overload is disabled for `outcome` itself so it
        *       never shadows the move constructor.
        */
        template<typename... Ts,
                 std::enable_if_t<!(sizeof...(Ts) == 1 &&
                     std::conjunction_v<std::is_same<std::decay_t<Ts>, outcome>...>), int> = 0>
        outcome(const Ts&... values) noexcept
        {
            const detail::result_region region = detail::current_result_region;
            // Values with no bound region == constructed outside on_complete: a
            // programming error. Flag it in debug; stay a no-op in release.
            assert((sizeof...(Ts) == 0 || region.data != nullptr) &&
                   "etask::core::outcome must be constructed by returning from on_complete");
            if (region.data == nullptr)
                return;
            _buffer = etools::memory::buffer<noop_deleter>{
                std::unique_ptr<std::byte[], noop_deleter>{region.data, noop_deleter{}},
                region.capacity
            };
            _buffer.pack(values...);
        }

        outcome(outcome&&) noexcept = default;
        outcome& operator=(outcome&&) noexcept = default;
        outcome(const outcome&) = delete;
        outcome& operator=(const outcome&) = delete;

        /// @brief Number of result bytes written into the region.
        [[nodiscard]] std::size_t size() const noexcept { return _buffer.size(); }
    };

} // namespace etask::core

#endif // ETASK_CORE_OUTCOME_HPP_
