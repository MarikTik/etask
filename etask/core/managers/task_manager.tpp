// SPDX-License-Identifier: MIT
/**
* @file task_manager.tpp
*
* @brief Implementation of task_manager.hpp's api.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-25
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_MANAGERS_TASK_MANAGER_TPP_
#define ETASK_CORE_MANAGERS_TASK_MANAGER_TPP_
#include "task_manager.hpp"

namespace etask::core::managers {

    template <typename I, typename P, typename S>
    task_manager<I, P, S>::task_manager(std::size_t max_task_load)
        : instant_base{max_task_load},
          polled_base{max_task_load},
          stateful_base{max_task_load}
    {
    }

    template <typename I, typename P, typename S>
    typename task_manager<I, P, S>::instant_t& task_manager<I, P, S>::instant() noexcept
    {
        return instant_base::tier();
    }

    template <typename I, typename P, typename S>
    typename task_manager<I, P, S>::polled_t& task_manager<I, P, S>::polled() noexcept
    {
        return polled_base::tier();
    }

    template <typename I, typename P, typename S>
    typename task_manager<I, P, S>::stateful_t& task_manager<I, P, S>::stateful() noexcept
    {
        return stateful_base::tier();
    }

    template <typename I, typename P, typename S>
    template <typename... Args>
    status_code task_manager<I, P, S>::register_task(
        channel_t *origin, std::uint8_t initiator_id, task_uid_t uid, Args&&... args)
    {
        const auto raw_uid = static_cast<raw_uid_t>(uid);

        // An instant command runs to completion right here; it never registers,
        // and it has no result, so `origin` and `initiator_id` do not apply.
        if constexpr (not std::is_same_v<instant_t, detail::absent_tier>) {
            if (instant_t::owns(raw_uid))
                return instant().register_task(uid, std::forward<Args>(args)...);
        }

        if constexpr (not std::is_same_v<polled_t, detail::absent_tier>) {
            if (polled_t::owns(raw_uid))
                return polled().register_task(origin, initiator_id, uid, std::forward<Args>(args)...);
        }

        if constexpr (not std::is_same_v<stateful_t, detail::absent_tier>) {
            if (stateful_t::owns(raw_uid))
                return stateful().register_task(origin, initiator_id, uid, std::forward<Args>(args)...);
        }

        return status_code::task_unknown;
    }

    template <typename I, typename P, typename S>
    status_code task_manager<I, P, S>::pause_task(task_uid_t uid)
    {
        const auto raw_uid = static_cast<raw_uid_t>(uid);

        if constexpr (not std::is_same_v<stateful_t, detail::absent_tier>) {
            if (stateful_t::owns(raw_uid))
                return stateful().pause_task(uid);
        }

        // A polled task is live but has no suspension to honor. Saying so is the
        // point of the tier split: the old single manager accepted this and called
        // an empty hook, so a caller could believe it had paused something.
        if constexpr (not std::is_same_v<polled_t, detail::absent_tier>) {
            if (polled_t::owns(raw_uid))
                return status_code::task_not_pausable;
        }

        return unroutable(raw_uid);
    }

    template <typename I, typename P, typename S>
    status_code task_manager<I, P, S>::resume_task(task_uid_t uid)
    {
        const auto raw_uid = static_cast<raw_uid_t>(uid);

        if constexpr (not std::is_same_v<stateful_t, detail::absent_tier>) {
            if (stateful_t::owns(raw_uid))
                return stateful().resume_task(uid);
        }

        if constexpr (not std::is_same_v<polled_t, detail::absent_tier>) {
            if (polled_t::owns(raw_uid))
                return status_code::task_not_pausable;
        }

        return unroutable(raw_uid);
    }

    template <typename I, typename P, typename S>
    status_code task_manager<I, P, S>::complete_task(task_uid_t uid, completion_reason reason)
    {
        const auto raw_uid = static_cast<raw_uid_t>(uid);

        // Concluding applies to both managed tiers - unlike pausing, it does not
        // require the task to be suspendable.
        if constexpr (not std::is_same_v<polled_t, detail::absent_tier>) {
            if (polled_t::owns(raw_uid))
                return polled().complete_task(uid, reason);
        }

        if constexpr (not std::is_same_v<stateful_t, detail::absent_tier>) {
            if (stateful_t::owns(raw_uid))
                return stateful().complete_task(uid, reason);
        }

        return unroutable(raw_uid);
    }

    template <typename I, typename P, typename S>
    void task_manager<I, P, S>::update()
    {
        // Instant commands are absent from this loop by construction: they never
        // survive the call that started them.
        polled().update();
        stateful().update();
    }

    template <typename I, typename P, typename S>
    constexpr status_code task_manager<I, P, S>::unroutable(raw_uid_t raw_uid) noexcept
    {
        if constexpr (not std::is_same_v<instant_t, detail::absent_tier>) {
            // A valid uid, but one that names a command which is never alive to be
            // addressed - as distinct from a managed task that simply is not
            // running right now.
            if (instant_t::owns(raw_uid))
                return status_code::task_not_addressable;
        }
        return status_code::task_unknown;
    }

} // namespace etask::core::managers

#endif // ETASK_CORE_MANAGERS_TASK_MANAGER_TPP_
