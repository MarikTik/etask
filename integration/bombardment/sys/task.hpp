/**
* @file task.hpp
*
* @brief Project task base aliases, bound to the generated task-id type.
*
* Every task scaffold in this tree derives from one of the aliases defined
* here. Binding them once, in one place, keeps the generated task files free
* of any direct dependency on the etask core templates - they name only the
* tier and `global::task_id`.
*
* A task's tier is what it *is*, and decides which lifecycle hooks it carries
* and what it costs:
*
* | Alias           | Hooks                                    | Costs         |
* |-----------------|------------------------------------------|---------------|
* | `instant_task`  | none - the constructor is the task       | nothing       |
* | `oneshot_task`  | on_execute, on_complete                  | one tick      |
* | `polled_task`   | + is_finished                            | polling       |
* | `stateful_task` | + on_pause, on_resume                    | suspension    |
*
* @note Generated once by etask, then owned by you. The `global::task_id`
*       enum these bind to is generated from your schema (see
*       ../generated/task_id.hpp); this file is not, and is never
*       overwritten once it exists.
*/
#ifndef SYS_TASK_HPP_
#define SYS_TASK_HPP_
#include <etask/core/tasks/tasks.hpp>
#include "../generated/task_id.hpp"

/**
* @brief A fire-and-forget command: it runs to completion inside the call that
* delivers it, then is destroyed. No lifecycle hooks, no vtable, no
* storage, no reply. Not a class template - it has no uid type to bind,
* because it has no virtual to dispatch.
*/
using instant_task  = etask::core::instant_task;

/**
* @brief Runs once and answers: on_execute() then on_complete(). is_finished()
* is sealed true, so the 'runs once' guarantee cannot be edited away.
*/
using oneshot_task  = etask::core::oneshot_task<global::task_id>;

/**
* @brief Runs across ticks and decides for itself when it is done, via
* is_finished(). Cannot be paused - that is a stateful_task.
*/
using polled_task   = etask::core::polled_task<global::task_id>;

/**
* @brief A polled task that can be suspended: on_pause() and on_resume()
* bracket a pause, and both are required, because deriving from this
* tier is a claim that the task holds something needing them.
*/
using stateful_task = etask::core::stateful_task<global::task_id>;

#endif // SYS_TASK_HPP_
