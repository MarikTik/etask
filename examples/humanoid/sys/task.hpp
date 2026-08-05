/**
* @file task.hpp
*
* @brief Project task base alias, bound to the generated task-id type.
*
* Every task scaffold in this tree derives from `task` (defined here).
* Binding it once, here, keeps the generated task files free of any direct
* dependency on the etask core template - they only ever name `task` and
* `global::task_id`.
*
* @note Generated once by etask, then owned by you. The `global::task_id`
*       enum it binds to is generated from your schema (see
*       ../generated/task_id.hpp); this alias is not, and is never
*       overwritten once it exists.
*/
#ifndef SYS_TASK_HPP_
#define SYS_TASK_HPP_
#include <etask/core/task.hpp>
#include "../generated/task_id.hpp"

/**
* @brief The base class for every task in this project.
*
* An `etask::core::task` specialized on this project's generated task id type.
*/
using task = etask::core::task<global::task_id>;

#endif // SYS_TASK_HPP_
