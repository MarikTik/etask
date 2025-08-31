// SPDX-License-Identifier: BSL-1.1
/**
* @file hub.hpp
*
* @brief Application wiring for the task framework: central place to list tasks and tune capacity.
*
* This header is part of the example scaffold and is intended to be edited by the user.
* It defines a single global task manager instance that the application code can use
* to register, run, and observe tasks. Modify this file when:
*  - adding or removing task types
*  - adjusting the expected maximum number of concurrently running tasks
*
* Usage model
*  - Include this header wherever you need to register or control tasks.
*  - Extend the tasks list in the template arguments to expose new task types.
*  - Tune the constructor argument to reflect the maximum number of tasks expected
*    to be alive concurrently; this value is used for preallocation.
*
* Customization points
*  1) Task set
*     Edit the template parameter pack to include all task types your application supports.
*     The order does not affect correctness, but the set must be unique and each task
*     must declare a `static constexpr uid` and derive from the expected task base.
*
*  2) Capacity
*     The integer passed to the task manager constructor sets the initial reserve.
*     For embedded builds, size this defensively to avoid growth at runtime.
* 
* @note
*  - This header is application-owned and expected to change from project to project.
*  - The task manager itself is not thread-safe; synchronize externally if needed.
*
* @author: Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-08-10
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE for details.
*/

#ifndef GLOBAL_TASK_MANAGER_HPP_
#define GLOBAL_TASK_MANAGER_HPP_
#include <etask/system/task_manager.hpp>
#include "../tasks/tasks.hpp"
namespace global{
    /**
    * @brief Application-global task manager instance.
    *
    * Modify the template arguments to add or remove task types.
    * Adjust the constructor argument to reflect the maximum number
    * of tasks expected to run concurrently.
    *
    * TODO: estimate the maximum simultaneous tasks for your application
    *       and set the reserve accordingly.
    */
    inline etask::system::task_manager<
        tasks::simple_task1,
        tasks::simple_task2
    > task_manager{2};  
}
#endif // GLOBAL_TASK_MANAGER_HPP_