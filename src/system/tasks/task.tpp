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

    template<typename TaskIDEnum>
    void task<TaskIDEnum>::on_start() {
        // Default implementation does nothing
    }
    
    template<typename TaskIDEnum>
    void task<TaskIDEnum>::on_execute() {
        // Default implementation does nothing
    }
    
    template<typename TaskIDEnum>
    bool task<TaskIDEnum>::is_finished() {
        return true; // Default implementation considers task finished immediately
    }
    
    template<typename TaskIDEnum>
    std::pair<tools::envelope, std::uint8_t> task<TaskIDEnum>::on_complete(bool interrupted) {
        // Default implementation returns empty envelope and status code 0
        return {tools::envelope{}, 0};
    }
    
    template<typename TaskIDEnum>
    void task<TaskIDEnum>::on_pause() {
        // Default implementation does nothing
    }
    
    template<typename TaskIDEnum>
    void task<TaskIDEnum>::on_resume() {
        // Default implementation does nothing
    }
    
}
#endif // ETASK_SYSTEM_TASKS_TASK_TPP_