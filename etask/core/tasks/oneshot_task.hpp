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
* This is @ref instant_task **with a return value**, and that is the whole idea.
* Like an instant command, the work happens in the **constructor**: the task is
* built from its parameters, does its job there, and is finished the moment it
* exists.
*
* What it does not share with `instant_task` is the ability to stay silent.
* Producing a reply requires a completion, and a completion requires the manager
* to own the task - so structurally it has to be a @ref polled_task. It is
* registered, `is_finished()` immediately says yes, and it completes on that same
* tick with `on_complete()` returning the result.
*
* Read a sensor, latch a value, run a self-test: anything whose whole job fits
* in the constructor but whose answer the caller wants back.
*
* If the caller does **not** want an answer, this is the wrong tier - that is a
* fire-and-forget command, and it belongs to @ref instant_task, which costs no
* vtable, no storage, and no tick at all.
*
* @note `on_execute()` is inherited from @ref polled_task, which declares it
*       pure, so a derived task must still define it - but it is **never
*       called**. `is_finished()` is polled before the manager decides whether to
*       execute, and it is sealed `true`, so the task concludes instead. An empty
*       body is the correct implementation; putting work there means it never
*       runs. Work belongs in the constructor, results in `on_complete()`.
*
* ## Why it is its own type
*
* Its whole content is `is_finished()` returning `true`, which a task could
* write by hand on a plain @ref polled_task. Making it a type buys two things a
* convention cannot:
*
* - **It states the intent.** "Done as soon as it is built" is a design
*   decision; spelling it in the type makes it visible at the declaration
*   instead of buried in a one-line method body.
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
    * @brief A polled task whose `is_finished()` is fixed at `true`: built,
    *        then completed on the same tick.
    *
    * ## Lifecycle
    *
    * - **constructor** - the task's whole job. It is finished as soon as it
    *   exists.
    * - `is_finished()` - fixed at `true`, sealed `final`. Not yours to override.
    * - `on_complete(reason)` - once, on the tick it was registered. Inherited
    *   from @ref task; override it to return the result.
    *
    * `on_execute()` must be defined, because @ref polled_task declares it pure,
    * but it is never called - leave it empty. See the note in this file's
    * overview.
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
        bool is_finished() final;
    };

} // namespace etask::core

#include "oneshot_task.tpp"
#endif // ETASK_CORE_TASKS_ONESHOT_TASK_HPP_
