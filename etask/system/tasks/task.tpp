/**
* @file task.tpp
*
* @brief implementation of task.tpp methods.
*
* @date 2025-07-03
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_SYSTEM_TASKS_TASK_TPP_
#define ETASK_SYSTEM_TASKS_TASK_TPP_
#include "task.hpp"

namespace etask::system::tasks {

    template<typename TaskID_t>
    void task<TaskID_t>::on_start() {
        // Default implementation does nothing
    }
    
    template<typename TaskID_t>
    void task<TaskID_t>::on_execute() {
        // Default implementation does nothing
    }
    
    template<typename TaskID_t>
    bool task<TaskID_t>::is_finished() {
        return true; // Default implementation considers task finished immediately
    }
    
    template<typename TaskID_t>
    std::pair<etools::memory::envelope<>, std::uint8_t> task<TaskID_t>::on_complete([[maybe_unused]] bool interrupted) {
        // Default implementation returns empty envelope and status code 0
        using uptr_t = std::unique_ptr<std::byte[], std::default_delete<std::byte[]>>;
        return { etools::memory::envelope<>{ uptr_t{}, 0 }, 0 };
    }
    
    template<typename TaskID_t>
    void task<TaskID_t>::on_pause() {
        // Default implementation does nothing
    }
    
    template<typename TaskID_t>
    void task<TaskID_t>::on_resume() {
        // Default implementation does nothing
    }
    
}
#endif // ETASK_SYSTEM_TASKS_TASK_TPP_