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

        // Constructible check is per-arm: a command whose constructor does not
        // accept these arguments is not a match, exactly as the storage-owning
        // managers treat a failed `emplace`.
        if constexpr (std::is_constructible_v<Task, Args...>) {
            // The command's entire life: constructed here, runs, and destroyed as
            // this scope exits. Nothing owns it, because nothing needs to.
            Task command{std::forward<Args>(args)...};
            (void)command;
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
