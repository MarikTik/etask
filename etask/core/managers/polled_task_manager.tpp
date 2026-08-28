// SPDX-License-Identifier: MIT
/**
* @file polled_task_manager.tpp
*
* @brief Implementation of polled_task_manager.hpp's api.
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
#ifndef ETASK_CORE_MANAGERS_POLLED_TASK_MANAGER_TPP_
#define ETASK_CORE_MANAGERS_POLLED_TASK_MANAGER_TPP_
#include "polled_task_manager.hpp"
#include <algorithm>
#include <cassert>

namespace etask::core::managers {

    template <std::size_t Budget, typename... Tasks>
    template<typename... Args>
    status_code polled_task_manager<Budget, Tasks...>::register_task(
        channel_t *origin, std::uint8_t initiator_id, task_uid_t uid, Args&&... args)
    {
        // A hook calling back in mid-sweep would mutate the set being walked.
        if (_in_update)
            return status_code::reentrancy_conflict;

        if (not origin)
            return status_code::channel_null;

        const auto raw_uid = static_cast<raw_uid_t>(uid);
        const auto max_concurrent = capacity_of(raw_uid);

        if (max_concurrent == 0)
            return status_code::task_unknown;

        const auto running_count = static_cast<std::size_t>(std::count_if(
            _tasks.begin(), _tasks.end(),
            [uid](const task_info& t_info) { return t_info.uid == uid; }
        ));

        if (running_count >= max_concurrent)
            return max_concurrent > 1 ? status_code::task_limit_reached : status_code::duplicate_task;

        // This task's own slots are free, but the tier as a whole is full: a
        // different condition from the one above, and one the caller fixes by
        // raising the budget rather than this task's capacity.
        if (_tasks.full())
            return status_code::task_budget_exhausted;

        auto handle = _registry.emplace(raw_uid, std::forward<Args>(args)...);

        if (not handle)
            return status_code::task_unknown;

        // Checked full() above, so this cannot fail; the handle would otherwise
        // leak its registry slot.
        [[maybe_unused]] const auto* record =
            _tasks.try_emplace_back(std::move(handle), initiator_id, uid, origin);
        assert(record and "static_vector rejected an emplace after full() said otherwise");
        return status_code::ok;
    }

    template <std::size_t Budget, typename... Tasks>
    status_code polled_task_manager<Budget, Tasks...>::complete_task(task_uid_t uid, completion_reason reason)
    {
        if (_in_update)
            return status_code::reentrancy_conflict;

        if (reason == completion_reason::finished)
            return status_code::invalid_completion_reason;

        auto it = find(uid);
        if (it == _tasks.end())
            return status_code::task_not_registered;

        if (it->task->is_finished())
            return status_code::task_already_finished;

        // Already concluding, for whatever reason - aborted or caller-supplied.
        // A task concludes once; a second request has nothing left to act on.
        if (it->reason != completion_reason::finished)
            return status_code::task_already_concluding;

        it->reason = reason;
        return status_code::ok;
    }

    template <std::size_t Budget, typename... Tasks>
    void polled_task_manager<Budget, Tasks...>::update()
    {
        const update_guard guard{_in_update};
        _garbage.reset();

        for (std::size_t i = 0; i < _tasks.size(); ++i) {
            auto &task_info = _tasks[i];
            auto &task = task_info.task;

            // Concluding, either because it was aborted or because it says it is
            // done. Either way the channel drives on_complete and disposes of the
            // result; the record is dropped at the end of the cycle.
            // `reason` is `finished` until complete_task names another, so anything
            // else means this task has been marked to conclude early.
            const bool concluding = task_info.reason != completion_reason::finished;
            if (concluding or task->is_finished()) {
                task_info.channel->complete(
                    task_info.initiator_id,
                    task_info.uid,
                    reply_status(task_info.reason),
                    task_info.reason,
                    *task);
                _garbage.set(i);
            }
            // Otherwise: one slice of work.
            else {
                task->on_execute();
            }
        }

        // Drop everything that concluded this cycle, back to front: swap_erase only
        // ever disturbs the erased index and the final slot, so walking downward
        // keeps every not-yet-examined index - and its garbage bit - valid. Costs
        // one move per *concluded* task rather than per survivor, which is what a
        // compacting erase would have charged on every tick.
        for (std::size_t i = _tasks.size(); i-- > 0; )
            if (_garbage.test(i))
                _tasks.swap_erase(i);
    }

    template <std::size_t Budget, typename... Tasks>
    typename polled_task_manager<Budget, Tasks...>::task_iterator
    polled_task_manager<Budget, Tasks...>::find(task_uid_t uid) noexcept
    {
        return std::find_if(_tasks.begin(), _tasks.end(),
            [uid](const task_info& t_info) { return t_info.uid == uid; }
        );
    }

    template <std::size_t Budget, typename... Tasks>
    constexpr std::size_t polled_task_manager<Budget, Tasks...>::capacity_of(raw_uid_t raw_uid) noexcept
    {
        std::size_t count = 0;
        (void)((detail::raw_uid_extractor<typename reg_t<Tasks>::type>::value == raw_uid
            ? (count = reg_t<Tasks>::count, true)
            : false) or ...);
        return count;
    }

    template <std::size_t Budget, typename... Tasks>
    constexpr bool polled_task_manager<Budget, Tasks...>::owns(raw_uid_t raw_uid) noexcept
    {
        return ((detail::raw_uid_extractor<typename reg_t<Tasks>::type>::value == raw_uid) or ...);
    }

    template <std::size_t Budget, typename... Tasks>
    polled_task_manager<Budget, Tasks...>::task_info::task_info(
        typename registry_t::handle_t&& task_in,
        std::uint8_t initiator_id_in,
        task_uid_t uid_in,
        channel_t *channel_in) noexcept
        : task{std::move(task_in)},
          initiator_id{initiator_id_in},
          uid{uid_in},
          channel{channel_in}
    {
    }

    template <std::size_t Budget, typename... Tasks>
    constexpr status_code polled_task_manager<Budget, Tasks...>::reply_status(completion_reason reason) noexcept
    {
        if (reason == completion_reason::finished)
            return status_code::task_finished;
        if (reason == completion_reason::aborted)
            return status_code::task_aborted;
        // A caller-supplied reason: concluded early, but not torn down mid-work.
        return status_code::task_completed_early;
    }

} // namespace etask::core::managers

#endif // ETASK_CORE_MANAGERS_POLLED_TASK_MANAGER_TPP_
