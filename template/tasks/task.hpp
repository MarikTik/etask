// SPDX-License-Identifier: MIT
/**
* @file task.hpp
*
* @brief Project task base alias, bound to the generated task-id type.
*
* Every task scaffold under this directory derives from `task` (defined here).
* Binding it once, here, keeps the generated task files free of any direct
* dependency on the etask core template - they only ever name `task` and
* `global::task_id`.
*
* @note User-owned. The `global::task_id` enum it binds to is generated from
*       your schema (see generated/task_id.hpp); this alias is not.
*/
#ifndef TASKS_TASK_HPP_
#define TASKS_TASK_HPP_
#include <etask/core/task.hpp>
#include "../generated/task_id.hpp"

/**
* @brief The base class for every task in this project.
*
* An `etask::core::task` specialized on this project's generated task id type.
*/
using task = etask::core::task<global::task_id>;

#endif // TASKS_TASK_HPP_
