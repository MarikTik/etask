// SPDX-License-Identifier: MIT
/**
* @file oneshot_task.hpp
*
* @brief Declares `etask::core::oneshot_task`, a polled task that concludes
*        after exactly one execution step.
*
* @ingroup etask_core etask::core::tasks
*
* ## The task that runs once and answers
*
* This is the "instant task that returns something" shape. It looks instant from
* the outside - do the thing, reply - but structurally it is a @ref polled_task,
* because producing a reply *requires* a completion, and a completion requires
* the manager to own the task long enough to drive it. So it is registered, it
* executes once on the next tick, and it completes.
*
* Read a sensor, latch a value, run a self-test: anything whose whole job fits
* in one step but whose answer the caller wants back.
*
* If the caller does **not** want an answer, this is the wrong tier - that is a
* fire-and-forget command, and it belongs to @ref instant_task, which costs no
* vtable, no storage, and no tick at all.
*
* ## Why it is its own type
*
* Its whole content is `is_finished()` returning `true`, which a task could
* write by hand on a plain @ref polled_task. Making it a type buys two things a
* convention cannot:
*
* - **It states the intent.** "Finishes after one step" is a design decision;
*   spelling it in the type makes it visible at the declaration instead of
*   buried in a one-line method body.
* - **It cannot be undone by accident.** `is_finished()` is `final` here, so a
*   later edit that adds a real termination condition - the sort of thing that
*   happens when a task grows - fails to compile instead of silently turning the
*   task into something that never finishes, or finishes at the wrong moment.
*
* @author
* Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-25
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/

#ifndef ETASK_CORE_TASKS_ONESHOT_TASK_HPP_
#define ETASK_CORE_TASKS_ONESHOT_TASK_HPP_
#include "polled_task.hpp"

namespace etask::core {

    /**
    * @class oneshot_task
    *
    * @brief A polled task whose `is_finished()` is fixed at `true`: one
    *        `on_execute()`, then completion.
    *
    * ## Lifecycle
    *
    * - `on_execute()` - the task's whole job, run once.
    * - `is_finished()` - fixed at `true`, sealed `final`. Not yours to override.
    * - `on_complete(reason)` - once, immediately after. Inherited from @ref task;
    *   override it to return the result.
    *
    * @tparam TaskID User-defined type identifying the concrete task type.
    */
    template<typename TaskID>
    struct oneshot_task : public polled_task<TaskID>
    {
        /**
        * @brief Always `true` - the task concludes after its single
        *        `on_execute()`.
        *
        * `final`: the "runs once" guarantee is the entire point of this tier, so
        * it is sealed rather than merely defaulted. A task that needs to decide
        * when it is done is a @ref polled_task.
        *
        * @return Always `true`.
        */
        bool is_finished() final { return true; }
    };

} // namespace etask::core

#endif // ETASK_CORE_TASKS_ONESHOT_TASK_HPP_
