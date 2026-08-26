// SPDX-License-Identifier: MIT
/**
* @file stateful_task_manager.tpp
*
* @brief Implementation of stateful_task_manager.hpp's api.
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
#ifndef ETASK_CORE_MANAGERS_STATEFUL_TASK_MANAGER_TPP_
#define ETASK_CORE_MANAGERS_STATEFUL_TASK_MANAGER_TPP_
#include "stateful_task_manager.hpp"
#include <algorithm>

namespace etask::core::managers {

    template <typename... Tasks>
    stateful_task_manager<Tasks...>::stateful_task_manager(std::size_t max_task_load)
    {
        _tasks.reserve(max_task_load);
    }

    template <typename... Tasks>
    template<typename... Args>
    status_code stateful_task_manager<Tasks...>::register_task(
        channel_t *origin, std::uint8_t initiator_id, task_uid_t uid, Args&&... args)
    {
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

        auto handle = _registry.emplace(raw_uid, std::forward<Args>(args)...);

        if (not handle)
            return status_code::task_unknown;

        _tasks.emplace_back(std::move(handle), initiator_id, uid, origin);
        return status_code::ok;
    }

    template <typename... Tasks>
    status_code stateful_task_manager<Tasks...>::reject_if_ending(task_info& info)
    {
        if (info.task->is_finished())
            return status_code::task_already_finished;

        if (info.reason != completion_reason::finished)
            return status_code::task_already_concluding;

        return status_code::ok;
    }

    template <typename... Tasks>
    status_code stateful_task_manager<Tasks...>::pause_task(task_uid_t uid)
    {
        auto it = find(uid);
        if (it == _tasks.end())
            return status_code::task_not_registered;

        if (const auto rejection = reject_if_ending(*it); rejection != status_code::ok)
            return rejection;

        // Suspended, or already on its way there: nothing further to ask for.
        if (it->state == detail::state::paused or it->state == detail::state::pausing)
            return status_code::task_already_paused;

        // Running, or with a resume still pending - either way the task is due to
        // be executing, so a pause is meaningful. A pending resume is simply
        // superseded: `on_resume()` never fires, because it never fired to begin
        // with, and the task goes straight back to being suspended.
        it->state = (it->state == detail::state::resuming) ? detail::state::paused : detail::state::pausing;
        return status_code::ok;
    }

    template <typename... Tasks>
    status_code stateful_task_manager<Tasks...>::resume_task(task_uid_t uid)
    {
        auto it = find(uid);
        if (it == _tasks.end())
            return status_code::task_not_registered;

        if (const auto rejection = reject_if_ending(*it); rejection != status_code::ok)
            return rejection;

        if (it->state == detail::state::running)
            return status_code::task_already_running;

        if (it->state == detail::state::resuming)
            return status_code::task_already_resumed;

        // Suspended, or with a pause still pending. A pending pause is superseded
        // the same way: `on_pause()` never fired, so there is nothing to undo and
        // the task simply keeps running.
        it->state = (it->state == detail::state::pausing) ? detail::state::running : detail::state::resuming;
        return status_code::ok;
    }

    template <typename... Tasks>
    status_code stateful_task_manager<Tasks...>::complete_task(task_uid_t uid, completion_reason reason)
    {
        if (reason == completion_reason::finished)
            return status_code::invalid_completion_reason;

        auto it = find(uid);
        if (it == _tasks.end())
            return status_code::task_not_registered;

        if (const auto rejection = reject_if_ending(*it); rejection != status_code::ok)
            return rejection;

        // Concluding is not gated on the run state: a suspended task may be
        // completed exactly as a running one may.
        it->reason = reason;
        return status_code::ok;
    }

    template <typename... Tasks>
    void stateful_task_manager<Tasks...>::update()
    {
        _garbage.reset();

        for (std::size_t i = 0; i < _tasks.size(); ++i) {
            auto &task_info = _tasks[i];
            auto &task = task_info.task;

            // `reason` is `finished` until complete_task names another, so anything
            // else means this task has been marked to conclude early.
            const bool concluding = task_info.reason != completion_reason::finished;

            // Ending takes priority over every other transition: a task that is
            // concluding is not paused, resumed, or executed first.
            if (concluding or task->is_finished()) {
                task_info.channel->complete(
                    task_info.initiator_id,
                    task_info.uid,
                    reply_status(task_info.reason),
                    task_info.reason,
                    *task);
                _garbage.set(i);
                continue;
            }

            switch (task_info.state) {
                // A pause was requested: honor it once, then settle as suspended.
                case detail::state::pausing:
                    task->on_pause();
                    task_info.state = detail::state::paused;
                    break;

                // A resume was requested: honor it once, then settle as running.
                // No on_execute() this tick - the task gets its slice next time,
                // exactly as a pause costs a tick.
                case detail::state::resuming:
                    task->on_resume();
                    task_info.state = detail::state::running;
                    break;

                // Suspended with nothing pending: left alone entirely.
                case detail::state::paused:
                    break;

                // The ordinary case: one slice of work.
                case detail::state::running:
                    task->on_execute();
                    break;
            }
        }

        // Drop everything that concluded this cycle.
        _tasks.erase(std::remove_if(_tasks.begin(), _tasks.end(),
                [index = 0, this]([[maybe_unused]] auto&&) mutable {
                    return _garbage.test(index++);
                }
            ),
            _tasks.end()
        );
    }

    template <typename... Tasks>
    typename stateful_task_manager<Tasks...>::task_iterator
    stateful_task_manager<Tasks...>::find(task_uid_t uid) noexcept
    {
        return std::find_if(_tasks.begin(), _tasks.end(),
            [uid](const task_info& t_info) { return t_info.uid == uid; }
        );
    }

    template <typename... Tasks>
    constexpr status_code stateful_task_manager<Tasks...>::reply_status(completion_reason reason) noexcept
    {
        if (reason == completion_reason::finished)
            return status_code::task_finished;
        if (reason == completion_reason::aborted)
            return status_code::task_aborted;
        // A caller-supplied reason: concluded early, but not torn down mid-work.
        return status_code::task_completed_early;
    }

    template <typename... Tasks>
    constexpr std::size_t stateful_task_manager<Tasks...>::capacity_of(raw_uid_t raw_uid) noexcept
    {
        std::size_t count = 0;
        (void)((detail::raw_uid_extractor<typename reg_t<Tasks>::type>::value == raw_uid
            ? (count = reg_t<Tasks>::count, true)
            : false) or ...);
        return count;
    }

    template <typename... Tasks>
    constexpr bool stateful_task_manager<Tasks...>::owns(raw_uid_t raw_uid) noexcept
    {
        return ((detail::raw_uid_extractor<typename reg_t<Tasks>::type>::value == raw_uid) or ...);
    }

    template <typename... Tasks>
    stateful_task_manager<Tasks...>::task_info::task_info(
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

} // namespace etask::core::managers

#endif // ETASK_CORE_MANAGERS_STATEFUL_TASK_MANAGER_TPP_
