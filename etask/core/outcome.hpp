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
* so an over-large result is dropped rather than corrupting memory - and, since
* dropping it silently would leave the peer decoding zeroed bytes, it is reported
* (see below).
*
* ## Carrying a status
*
* By default the reply's `status_code` is the manager's (`task_finished` for a
* natural completion, `task_aborted` for a forced one). A task that wants the
* peer to discriminate on something finer - which is what lets the Python
* receiver know *which result shape* it is looking at - overrides it:
* ```cpp
* return outcome{last_good_reading}.with_status(status_code::task_io_error);
* ```
* @ref with_status chains off the temporary so it still reads as one `return`.
* The channel writes the reply's code byte **after** `on_complete`, so a
* task-chosen status lands on the wire (@ref etask::core::protocol::reply::set_code).
* An outcome that names nothing reports `status_code::ok`, which is the one code
* @ref with_status will not accept - so "the task chose nothing" and "the task
* chose this" never have to be told apart by a second flag.
*
* An over-large result sets that status itself: see @ref status_code::result_too_large.
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
#include <utility>
#include <eser/flat/size.hpp>
#include <etools/memory/buffer.hpp>
#include "status_code.hpp"
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

        /**
        * @brief The status this outcome puts on the reply.
        *
        * `ok` is the "nothing chosen" value: a completing task can never name it
        * (@ref with_status rejects the whole manager/API range, of which `ok` is
        * a member), so it needs no separate "was it set" flag.
        */
        status_code _status{status_code::ok};

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
        *
        * @warning If the values do not fit the designated region, **nothing is
        *       packed**: the result stays empty and this outcome forces
        *       @ref status_code::result_too_large onto the reply, so the peer
        *       learns why it got no data instead of decoding zeroed bytes. Debug
        *       builds assert first - a result that cannot fit its packet is a
        *       schema/packet-size mismatch to fix at build time, not to ship.
        */
        template<typename... Ts,
                 std::enable_if_t<!(sizeof...(Ts) == 1 &&
                     std::conjunction_v<std::is_same<std::decay_t<Ts>, outcome>...>), int> = 0>
        outcome(const Ts&... values) noexcept;

        outcome(outcome&&) noexcept = default;
        outcome& operator=(outcome&&) noexcept = default;
        outcome(const outcome&) = delete;
        outcome& operator=(const outcome&) = delete;

        /**
        * @brief Overrides the reply's status code, chaining off the `return`.
        *
        * ```cpp
        * return outcome{fix}.with_status(status_code::task_validation_failed);
        * ```
        * Without this the reply carries the manager's own status
        * (`task_finished` / `task_aborted`). With it, the peer - notably the
        * Python receiver - can tell which of a task's result shapes it holds.
        *
        * @param code The status to put on the wire. Use the task range
        *        (`is_task_status`) or the custom range (`is_custom_status`); a
        *        manager/API code (`is_manager_status`) means "the manager
        *        rejected the request, no task ran", so a completing task must
        *        not claim one - `ok` least of all, since that is precisely how
        *        an outcome says it chose nothing. Debug builds assert this.
        * @return This outcome, moved, so it can be returned directly.
        *
        * @note Rvalue-qualified: it exists to be used on the temporary in a
        *       `return`, not to mutate a named outcome after the fact.
        */
        outcome&& with_status(status_code code) && noexcept;

        /**
        * @brief The status this outcome puts on the reply.
        * @return The task's chosen status, or `status_code::ok` when it chose
        *         none - in which case the manager's own code (`task_finished` /
        *         `task_aborted`) stands.
        */
        [[nodiscard]] status_code status() const noexcept;

        /// @brief Number of result bytes written into the region.
        [[nodiscard]] std::size_t size() const noexcept;
    };

} // namespace etask::core

#include "outcome.tpp"
#endif // ETASK_CORE_OUTCOME_HPP_
