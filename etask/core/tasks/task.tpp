// SPDX-License-Identifier: MIT
/**
* @file task.tpp
*
* @brief Implementation of task.hpp's default hook.
*
* @date 2026-08-25
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_TASKS_TASK_TPP_
#define ETASK_CORE_TASKS_TASK_TPP_
#include "task.hpp"

namespace etask::core {

    template<typename TaskID>
    outcome task<TaskID>::on_complete([[maybe_unused]] completion_reason reason) {
        // Default implementation returns an empty result.
        return {};
    }

} // namespace etask::core
#endif // ETASK_CORE_TASKS_TASK_TPP_
