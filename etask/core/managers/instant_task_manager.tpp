// SPDX-License-Identifier: MIT
/**
* @file instant_task_manager.tpp
*
* @brief Implementation of instant_task_manager.hpp's api.
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
#ifndef ETASK_CORE_MANAGERS_INSTANT_TASK_MANAGER_TPP_
#define ETASK_CORE_MANAGERS_INSTANT_TASK_MANAGER_TPP_
#include "instant_task_manager.hpp"

namespace etask::core::managers {

    template <typename... Tasks>
    template <typename Task, typename... Args>
    bool instant_task_manager<Tasks...>::run_if_matching(raw_uid_t raw_uid, Args&&... args)
    {
        if (detail::raw_uid_extractor<Task>::value != raw_uid)
            return false;

        // Two ways to build the command, tried in that order:
        //
        //  - natively, when the caller already holds typed arguments. This is
        //    the in-process path (`internal_channel`), and it is preferred: the
        //    arguments are right there, so round-tripping them through a payload
        //    would be pure loss.
        //  - through the unpacking adapter, when the caller holds the request's
        //    raw bytes. This is the wire path, and it is the only one that can
        //    turn a `buffer_view` into a native-ctor command's arguments.
        //
        // A command matching neither is not a match for these arguments at all,
        // exactly as the storage-owning managers treat a failed `emplace`.
        using stored_t = typename detail::registered_task<Task>::type;

        if constexpr (std::is_constructible_v<Task, Args...>) {
            // The command's entire life: constructed here, runs, and destroyed as
            // this scope exits. Nothing owns it, because nothing needs to.
            [[maybe_unused]] Task command{std::forward<Args>(args)...};
            return true;
        }
        else if constexpr (std::is_constructible_v<stored_t, Args...>) {
            [[maybe_unused]] stored_t command{std::forward<Args>(args)...};
            return true;
        }
        else {
            return false;
        }
    }

    template <typename... Tasks>
    template <typename... Args>
    status_code instant_task_manager<Tasks...>::register_task(task_uid_t uid, Args&&... args)
    {
        const auto raw_uid = static_cast<raw_uid_t>(uid);

        // Short-circuits on the first matching arm, so exactly one command is
        // constructed - and only that one's constructor is instantiated.
        const bool ran = (run_if_matching<Tasks>(raw_uid, std::forward<Args>(args)...) or ...);

        return ran ? status_code::ok : status_code::task_unknown;
    }

    template <typename... Tasks>
    constexpr bool instant_task_manager<Tasks...>::owns(raw_uid_t raw_uid) noexcept
    {
        return ((detail::raw_uid_extractor<Tasks>::value == raw_uid) or ...);
    }

} // namespace etask::core::managers

#endif // ETASK_CORE_MANAGERS_INSTANT_TASK_MANAGER_TPP_
