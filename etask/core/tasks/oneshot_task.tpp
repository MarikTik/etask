// SPDX-License-Identifier: MIT
/**
* @file oneshot_task.tpp
*
* @brief Implementation of oneshot_task.hpp's sealed completion predicate.
*
* @date 2026-08-25
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_TASKS_ONESHOT_TASK_TPP_
#define ETASK_CORE_TASKS_ONESHOT_TASK_TPP_
#include "oneshot_task.hpp"

namespace etask::core {

    template<typename TaskID>
    bool oneshot_task<TaskID>::is_finished() {
        return true; // Sealed: the constructor was the whole job, so it is already done.
    }

} // namespace etask::core
#endif // ETASK_CORE_TASKS_ONESHOT_TASK_TPP_
