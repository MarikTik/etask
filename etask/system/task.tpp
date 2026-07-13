// SPDX-License-Identifier: BSL-1.1
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
#ifndef ETASK_SYSTEM_TASK_TPP_
#define ETASK_SYSTEM_TASK_TPP_
#include "task.hpp"

namespace etask::system {

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
    etools::memory::buffer<> task<TaskID_t>::on_complete([[maybe_unused]] completion_reason reason) {
        // Default implementation returns an empty result buffer.
        return etools::memory::buffer<>{};
    }
    
    template<typename TaskID_t>
    void task<TaskID_t>::on_pause() {
        // Default implementation does nothing
    }
    
    template<typename TaskID_t>
    void task<TaskID_t>::on_resume() {
        // Default implementation does nothing
    }
    
} // etask::system
#endif // ETASK_SYSTEM_TASK_TPP_