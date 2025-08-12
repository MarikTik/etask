/**
* @file task_manager.tpp
*
* @brief implementation of task_manager.tpp methods.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-09
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_SYSTEM_MANAGMENT_TASK_MANAGER_TPP_
#define ETASK_SYSTEM_MANAGMENT_TASK_MANAGER_TPP_
#include "task_manager.hpp"
#include <algorithm>

namespace etask::system::management {

    template <typename Allocator, typename... Tasks>
    task_manager<Allocator, Tasks...>::task_manager(std::size_t max_task_load)
    {
        _tasks.reserve(max_task_load * _load_factor);
    }

    template <typename Allocator, typename... Tasks>
    status_code task_manager<Allocator, Tasks...>::register_task(channel_t *origin, uint8_t initiator_id, task_uid_t uid, etools::memory::envelope_view params)
    {
        task_t *task = _registry.construct(uid, std::move(params));
        if (not task) return status_code::task_not_existing;

        _tasks.emplace_back(task, tasks::state{}, initiator_id, uid, origin);

        return status_code::ok;
    }

    template <typename Allocator, typename... Tasks>
    status_code task_manager<Allocator, Tasks...>::pause_task(task_uid_t uid)
    {
        auto it = find(uid);

        if (it == _tasks.cend()) 
            return status_code::task_not_registered;
        auto &task_state = it->state;

        if (task_state.is_paused()) 
            return status_code::task_already_paused;
        task_state.set_paused();
        return status_code::ok;
    }

    template <typename Allocator, typename... Tasks>
    status_code task_manager<Allocator, Tasks...>::resume_task(task_uid_t uid)
    {
        auto it = find(uid);
        if (it == _tasks.cend()) 
            return status_code::task_not_registered;
        auto &task_state = it->state;
        task_state.set_resumed();
        return status_code::ok;
    }

    template <typename Allocator, typename... Tasks>
    status_code task_manager<Allocator, Tasks...>::abort_task(task_uid_t uid)
    {
        auto it = find(uid);
        if (it == _tasks.cend()) return status_code::task_not_registered; // Task not found
        auto &task_state = it->state;
        task_state.set_aborted();
        return status_code::ok;
    }

    template <typename Allocator, typename... Tasks>
    void task_manager<Allocator, Tasks...>::update()
    {
        _garbage.reset();
        for (std::size_t i = 0; i < _tasks.size(); ++i) {
            auto &task_info = _tasks[i];
            auto &task = task_info.task;
            auto &state = task_info.state;
            auto initiator_id = task_info.state;
            auto task_uid = task_info.uid;
            auto *channel = task_info.channel;

            if (state.is_paused()){
                if (state.is_running()){
                    task->on_pause();
                    state.set_idle();
                }
            }
            else if (state.is_aborted()){
                const auto&& [result, status_code] = task->on_complete(true);
                channel->on_result(initiator_id, task_uid, std::move(result), status_code);
                _garbage.set(i);
            }
            else if (task->is_finished()){
                const auto&& [result, status_code] = task->on_complete(false);
                channel->on_result(initiator_id, task_uid, std::move(result), status_code);
                _garbage.set(i);
            }
            else{
                if (state.is_resumed() and state.is_idle()){
                    task->on_start();
                    state.set_started();
                }
                else if (state.is_started()){
                    task->on_execute();
                }
                else {
                    task->on_start();
                    state.set_started();
                }
            }
        }

        _tasks.erase(
            std::remove_if(_tasks.begin(), _tasks.end(),
                [index = 0, this](auto&&) mutable {
                    return _garbage.test(index++);
                }
            ),
            _tasks.end()
        );
        _garbage.clear();
    }

    template <typename Allocator, typename... Tasks>
    typename task_manager<Allocator, Tasks...>::task_iterator
    task_manager<Allocator, Tasks...>::find(task_uid_t uid) noexcept
    {
        return std::find_if(_tasks.begin(), _tasks.end(),
            [uid](const task_info& t_info) { return t_info.uid == uid; }
        );
    }

    template <typename Allocator, typename... Tasks>
    constexpr task_manager<Allocator, Tasks...>::task_info::task_info(task_t * task_in, tasks::state state_in, uint8_t initiator_id_in, task_uid_t uid_in, channel_t *channel_in) noexcept
        : task(task_in),
              state(state_in),
              initiator_id(initiator_id_in),
              uid(uid_in),
              channel(channel_in)
    {
    }
}

#endif // ETASK_SYSTEM_MANAGMENT_TASK_MANAGER_TPP_