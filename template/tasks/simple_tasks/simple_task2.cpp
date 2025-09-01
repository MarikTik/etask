// SPDX-License-Identifier: BSL-1.1
/**
* @file simple_task2.cpp
*
* @note this is an example file, feel free to remove it in your project.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-08-14
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef TASKS_SIMPLE1_TASK_HPP_
#define TASKS_SIMPLE1_TASK_HPP_
#include "../task.hpp"
#include "simple_task2.hpp"

namespace tasks {
 
    simple_task2::simple_task2([[maybe_unused]] etools::memory::envelope_view env) noexcept
    {
        // discard env since no parameter are expected by the task
    }
    void simple_task2::on_start()
    {
        // Initialization logic can be added here if needed
    }
}
// namespace tasks
#endif // TASKS_SIMPLE1_TASK_HPP_