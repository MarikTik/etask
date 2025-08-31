// SPDX-License-Identifier: BSL-1.1
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
#ifndef ETASK_SYSTEM_TASK_MANAGER_TPP_
#define ETASK_SYSTEM_TASK_MANAGER_TPP_
#include "task_manager.hpp"
#include <algorithm>

namespace etask::system {

    template <typename Allocator, typename... Tasks>
    task_manager<Allocator, Tasks...>::task_manager(std::size_t max_task_load)
    {
        _tasks.reserve(max_task_load);
    }

    template <typename Allocator, typename... Tasks>
    status_code task_manager<Allocator, Tasks...>::register_task(channel_t *origin, uint8_t initiator_id, task_uid_t uid, etools::memory::envelope_view params)
    {
        if (not origin)
            return status_code::channel_null;

        if (find(uid) not_eq _tasks.end())
            return status_code::duplicate_task;

        using raw_uid_t = typename std::conditional_t<
            std::is_enum_v<task_uid_t>,
            std::underlying_type<task_uid_t>,
            etools::meta::type_identity<task_uid_t>
        >::type;

        const auto raw_uid = static_cast<raw_uid_t>(uid);
        task_t *task = _registry.emplace(raw_uid, std::move(params));
 
        if (not task) 
            return status_code::task_unknown;

        _tasks.emplace_back(task, state{}, initiator_id, uid, origin);
        return status_code::ok;
    }

    template <typename Allocator, typename... Tasks>
    status_code task_manager<Allocator, Tasks...>::pause_task(task_uid_t uid)
    {
        auto it = find(uid);
        if (it == _tasks.end())
            return status_code::task_not_registered;
        
        auto &state = it->state;
        
        if (it->task->is_finished())
            return status_code::task_already_finished;

        if (state.is_aborted())
            return status_code::task_already_aborted;
        
        if (state.is_paused())
            return status_code::task_already_paused;

        if (not state.is_started())
            return status_code::task_not_running;
            
        state.set_paused();
        return status_code::ok;
    }
    
    template <typename Allocator, typename... Tasks>
    status_code task_manager<Allocator, Tasks...>::resume_task(task_uid_t uid)
    {
        auto it = find(uid);

        if (it == _tasks.end())
            return status_code::task_not_registered;
        
        auto &state = it->state;

        if (it->task->is_finished())
            return status_code::task_already_finished;

        if (state.is_aborted())
            return status_code::task_already_aborted;

        if (state.is_running())
            return status_code::task_already_running;

        if (state.is_resumed())
            return status_code::task_already_resumed;

        state.set_resumed();
        return status_code::ok;
    }

    template <typename Allocator, typename... Tasks>
    status_code task_manager<Allocator, Tasks...>::abort_task(task_uid_t uid)
    {
        auto it = find(uid);
        if (it == _tasks.end()) 
            return status_code::task_not_registered;
        
        auto &state = it->state;

        if (it->task->is_finished())
            return status_code::task_already_finished;

        if (state.is_aborted())
            return status_code::task_already_aborted;

        state.set_aborted();
        return status_code::ok;
    }

    template <typename Allocator, typename... Tasks>
    void task_manager<Allocator, Tasks...>::update()
    {
        // zero `_garbage` bitset before loop entry.
        _garbage.reset();

        for (std::size_t i = 0; i < _tasks.size(); ++i) {
            auto &task_info = _tasks[i];
            auto &task = task_info.task;
            auto &state = task_info.state;
            auto initiator_id = task_info.initiator_id;
            auto task_uid = task_info.uid;
            auto *channel = task_info.channel;

            // Option 0 - task was just registered and is idle.
            // call `on_start()` and set `running` and `started` flags
            if (state.is_idle() and not state.is_started()){
                state.set_running().set_started();
                task->on_start();
            }
            // Option 1 - task is aborted, exit task by calling
            // `on_complete(interrupted=true)` and communicate the result 
            // through the channel.
            if (state.is_aborted()){
                const auto&& [result, status_code] = task->on_complete(true);
                channel->on_result(initiator_id, task_uid, std::move(result), status_code);
                _garbage.set(i);
            }
            // Option 2 - task is finished, exit task by calling
            // `on_complete(interrupted=false)` and communicate the result
            // through the channel.
            else if (task->is_finished()){
                const auto&& [result, status_code] = task->on_complete(false);
                channel->on_result(initiator_id, task_uid, std::move(result), status_code);
                _garbage.set(i);
            }
            // Option 3 - task is paused, check if there is a 
            // need to call `on_pause()` (only once).
            else if (state.is_paused() and state.is_running()){
                task->on_pause();
                state.set_idle(); // also resets `running` flag.
            }
            // Option 4 - task is resumed, check if there is a 
            // need to call `on_resume()` (only once).
            else if (state.is_resumed() and state.is_idle()){
                task->on_resume();
                state.set_running();
            }
            // Option 5 - task should continue in execution mode
            // and call `on_execute()` since no other flags were 
            // initiated.
            else {
                task->on_execute();
            }
        }
        
        // Clean pipeline, remove all finished/aborted tasks from _`tasks`.
        _tasks.erase(std::remove_if(_tasks.begin(), _tasks.end(),
                [index = 0, this]([[maybe_unused]] auto&&) mutable {
                    return _garbage.test(index++);
                }
            ),
            _tasks.end()
        );
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
    constexpr task_manager<Allocator, Tasks...>::task_info::task_info(task_t * task_in, system::state state_in, uint8_t initiator_id_in, task_uid_t uid_in, channel_t *channel_in) noexcept
        : task{task_in},
          state{state_in},
          initiator_id{initiator_id_in},
          uid{uid_in},
          channel{channel_in}
    {
    }
}

#endif // ETASK_SYSTEM_TASK_MANAGER_TPP_