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
        // Sealed: the task concludes after its single on_execute().
        //
        // The manager polls this BEFORE deciding whether to execute - a task that
        // reports finished is concluded instead of run - so answering `true` here
        // on the first poll would conclude the task without ever executing it.
        // Answer `false` once, which spends this tick on the single on_execute(),
        // then `true` on the next poll, which concludes it.
        if (not _executed) {
            _executed = true;
            return false;
        }
        return true;
    }

} // namespace etask::core
#endif // ETASK_CORE_TASKS_ONESHOT_TASK_TPP_
