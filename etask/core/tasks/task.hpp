// SPDX-License-Identifier: MIT
/**
* @file task.hpp
*
* @brief Declares `etask::core::task`, the polymorphic base every *managed*
*        task shares.
*
* @ingroup etask_core etask::core::tasks
*
* This is the root of the managed-task hierarchy - the type the manager owns
* tasks through and the type `channel::complete` is handed. It carries the two
* things that are true of **every** task the framework keeps alive across ticks
* and nothing else:
*
* - a virtual destructor, because the manager owns tasks through this base;
* - `on_complete(completion_reason)`, because every managed task concludes, on
*   every path, exactly once.
*
* Everything else - execution, polling, pause/resume - belongs to a tier below
* (see @ref polled_task, @ref stateful_task), so a task never inherits a vtable
* slot for a hook it does not use.
*
* ## Not every task is a `task`
*
* @ref instant_task is deliberately **not** part of this hierarchy. A fire-and-
* forget command has no completion, so it has nothing to put here - and having
* nothing to put here means it needs no vtable at all. It is a separate, non-
* polymorphic kind, run by its own manager. See @ref instant_task.
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
*
* @par Changelog
* - 2026-08-25
*      - Split out of the former single six-hook `etask::core::task`. `on_start`
*        is gone from the framework entirely (a task is a runtime object created
*        after all initialization, so its constructor is the setup point);
*        `on_execute`/`is_finished` moved down to @ref polled_task and
*        `on_pause`/`on_resume` to @ref stateful_task.
*/

#ifndef ETASK_CORE_TASKS_TASK_HPP_
#define ETASK_CORE_TASKS_TASK_HPP_
#include "../outcome.hpp"
#include "../completion_reason.hpp"

namespace etask::core {

    /**
    * @class task
    *
    * @brief Base of every managed task: a virtual destructor and a completion.
    *
    * Tasks are never driven directly by user code. The manager invokes the
    * lifecycle hooks; a task's job is to implement them.
    *
    * A task derived *directly* from `task` runs no execution steps at all - it
    * is registered, it concludes on the next `update()`, and its result is sent.
    * That is a legitimate shape, but @ref oneshot_task says the same thing more
    * clearly and guarantees it structurally, so prefer it.
    *
    * @tparam TaskID User-defined type (commonly an enum) identifying the
    *         concrete task type. Each task class declares its own
    *         `static constexpr TaskID uid`.
    */
    template<typename TaskID>
    struct task
    {
        /**
        * @brief Conclude the task and produce its result. Runs exactly once.
        *
        * Invoked by the manager as the task ends, on every path: natural
        * completion (after `is_finished()` returned true) or a forced completion
        * requested through a channel. Branch on `reason` to decide what to return.
        *
        * The channel - not the task - owns where the result lands: it designates
        * the destination region before this call, so the returned @ref outcome is
        * serialized straight into the outgoing packet with no heap and no copy.
        *
        * @param reason Why the task is concluding. A system-only, input-only
        *               value that exists purely for this call: it is never stored,
        *               returned, or forwarded. `completion_reason::finished` for
        *               natural completion; `completion_reason::aborted` or a
        *               caller-supplied reason for a forced one.
        *
        * @return An @ref outcome carrying the result values - write it as
        *         `return {v1, v2, ...}`, or `return {}` for no result. Name a
        *         non-default reply status with `.with_status(code)`.
        *
        * The base implementation returns an empty result.
        */
        virtual outcome on_complete([[maybe_unused]] completion_reason reason);

        /**
        * @brief Virtual destructor - the manager owns tasks through this base.
        */
        virtual ~task() = default;
    };

} // namespace etask::core

#include "task.tpp"
#endif // ETASK_CORE_TASKS_TASK_HPP_
