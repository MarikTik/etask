// SPDX-License-Identifier: MIT
/**
* @file polled_task.hpp
*
* @brief Declares `etask::core::polled_task`, a task the manager drives across
*        ticks until it reports itself finished.
*
* @ingroup etask_core etask::core::tasks
*
* A polled task is the ordinary "work that takes a while" task: the manager
* calls `on_execute()` on every `update()` and asks `is_finished()` whether to
* keep going. When it answers true, `on_complete()` runs and the result is sent.
*
* It adds exactly the two hooks that polling needs, on top of the completion it
* inherits from @ref task. It does **not** carry `on_pause`/`on_resume`: a task
* that must survive being suspended is a @ref stateful_task.
*
* ## Both hooks are pure
*
* `on_execute()` and `is_finished()` are pure virtual, deliberately. A default
* `is_finished()` returning `true` would make "I forgot to write my termination
* condition" indistinguishable from "I meant this to finish at once" - the task
* would quietly conclude after one tick and look like it worked. The second
* intent has its own type (@ref oneshot_task) that states it explicitly and
* enforces it, so the default has no honest use left and only hides the mistake.
* A polled task with no execution step is likewise not a polled task.
*
* `on_complete()` stays defaulted on @ref task, because "concludes with no
* result" *is* a real answer there - it is what a task with no `returns:` in the
* schema means.
*
* ## There is no `on_start`
*
* Setup belongs in the constructor. A task is a runtime object built by
* `register_task` long after every board-level initialization has run, so the
* classic "can't do this at construction time" reason does not apply here.
* Anything a task needs before its first execution step it can do when it is
* built, with its parameters and its scope context already in hand.
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

#ifndef ETASK_CORE_TASKS_POLLED_TASK_HPP_
#define ETASK_CORE_TASKS_POLLED_TASK_HPP_
#include "task.hpp"

namespace etask::core {

    /**
    * @class polled_task
    *
    * @brief A task executed incrementally and polled for completion.
    *
    * ## Lifecycle
    *
    * - `on_execute()` - one slice of work, every tick, until finished.
    * - `is_finished()` - polled after each `on_execute()`.
    * - `on_complete(reason)` - once, at the end. Inherited from @ref task.
    *
    * @tparam TaskID User-defined type identifying the concrete task type.
    */
    template<typename TaskID>
    struct polled_task : public task<TaskID>
    {
        /**
        * @brief One slice of work, run on every `update()` tick.
        *
        * Must not block: do a little and return, so other tasks get their turn.
        * Keeps being called until `is_finished()` returns true or the task is
        * completed externally.
        *
        * Pure: a polled task with nothing to execute is not a polled task.
        */
        virtual void on_execute() = 0;

        /**
        * @brief Whether the task is done; polled after each `on_execute()`.
        *
        * @return `true` once there is no work left - the manager then calls
        *         `on_complete()` and removes the task; `false` to keep running.
        *
        * Pure, so the termination condition is always a decision the task
        * actually made. To finish unconditionally after one step, derive from
        * @ref oneshot_task, which says so and enforces it.
        */
        virtual bool is_finished() = 0;
    };

} // namespace etask::core

#endif // ETASK_CORE_TASKS_POLLED_TASK_HPP_
