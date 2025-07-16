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
    bool task_manager<Allocator, Tasks...>::register_task(channel_t *origin, task_uid_t uid, tools::envelope params)
    {
        auto it = std::lower_bound(_task_table.cbegin(), _task_table.cend(), uid,
            [](const auto &entry, const auto &value){
                return entry.value < value;
            }
        );

        if (it == _task_table.cend() or it->value not_eq uid) return false; // UID not found

        _tasks.emplace_back(std::make_tuple(
            it->constructor(params),
            {},
            uid,
            origin
        ));

        return true;
    }

    template <typename Allocator, typename... Tasks>
    bool task_manager<Allocator, Tasks...>::pause_task(task_uid_t uid)
    {
        auto it = std::find_if(_tasks.cbegin(), _tasks.cend(),
            [uid](const task_info_t &task_info) {
                return std::get<2>(task_info) == uid;
            }
        );
        if (it == _tasks.cend()) return false; // Task not found

        auto &task_state = std::get<1>(*it);
        task_state.set_paused();
        return true;
    }

    template <typename Allocator, typename... Tasks>
    bool task_manager<Allocator, Tasks...>::resume_task(task_uid_t uid)
    {
        auto it = std::find_if(_tasks.cbegin(), _tasks.cend(),
            [uid](const task_info_t &task_info) {
                return std::get<2>(task_info) == uid;
            }
        );
        if (it == _tasks.cend()) return false; // Task not found
        auto &task_state = std::get<1>(*it);
        task_state.set_resumed();
        return true;
    }

    template <typename Allocator, typename... Tasks>
    bool task_manager<Allocator, Tasks...>::abort_task(task_uid_t uid)
    {
        auto it = std::find_if(_tasks.cbegin(), _tasks.cend(),
            [uid](const task_info_t &task_info) {
                return std::get<2>(task_info) == uid;
            }
        );
        if (it == _tasks.cend()) return false; // Task not found
        auto &task_state = std::get<1>(*it);
        task_state.set_aborted();
        return true;
    }

    template <typename Allocator, typename... Tasks>
    void task_manager<Allocator, Tasks...>::update()
    {
        _garbage.reset();
        for (std::size_t i = 0; i < _tasks.size(); ++i) {
            auto &task_info = _tasks[i];
            auto &[task, state, uid, channel] = task_info;

            if (state.is_paused()){
                if (state.is_running()){
                    task->on_pause();
                    state.set_idle();
                }
            }
            else if (state.is_aborted()){
                const auto&& [result, status_code] = task->on_complete(true);
                channel->on_result(result, status_code);
                _garbage.set(i);
            }
            else if (task->is_finished()){
                const auto&& [result, status_code] = task->on_complete(false);
                channel->on_result(result, status_code);
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
                [index = 0, this](const task_info_t &task_info) mutable {
                    return _garbage.test(index++);
                }
            ),
            _tasks.end()
        );
        _garbage.clear();
    }
}

#endif // ETASK_SYSTEM_MANAGMENT_TASK_MANAGER_TPP_