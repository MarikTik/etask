// SPDX-License-Identifier: MIT
/**
* @file stateful_task.hpp
*
* @brief Declares `etask::core::stateful_task`, a polled task that can be
*        suspended and resumed.
*
* @ingroup etask_core etask::core::tasks
*
* A stateful task is a @ref polled_task that survives being paused. It adds the
* two hooks that bracket a suspension: `on_pause()` to make the paused state
* safe, and `on_resume()` to put things back.
*
* The name is the criterion. Pause/resume only mean anything if there is state
* that must not simply persist unattended across the gap - a motor that has to
* stop, a bus that has to be released, an integrator that has to be frozen. A
* task with nothing to protect gains nothing here and should stay a
* @ref polled_task, where it costs no vtable slots for hooks it leaves empty.
*
* ## Both hooks are pure
*
* Deriving from this tier is a claim: *this task holds something that must be
* handled before it is suspended.* Defaulted no-op hooks would let a task make
* that claim and then not honor it - paying for two vtable slots while doing
* nothing to make the paused state safe, which is precisely the failure the tier
* exists to prevent. Pure virtual makes the claim and the implementation
* inseparable. A task with nothing to write here belongs one tier up.
*
* This is the only tier the manager will accept a pause or resume directive for.
* Aimed at any other tier, those directives are answered with
* `status_code::task_not_pausable`.
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

#ifndef ETASK_CORE_TASKS_STATEFUL_TASK_HPP_
#define ETASK_CORE_TASKS_STATEFUL_TASK_HPP_
#include "polled_task.hpp"

namespace etask::core {

    /**
    * @class stateful_task
    *
    * @brief A polled task that can be paused and resumed.
    *
    * ## Lifecycle
    *
    * - `on_execute()` / `is_finished()` - the polling loop, from @ref polled_task.
    * - `on_pause()` - once, when the task is paused.
    * - `on_resume()` - once, when it resumes.
    * - `on_complete(reason)` - once, at the end. From @ref task.
    *
    * While paused, `on_execute()` is not called; the task is idle until resumed
    * or completed.
    *
    * @tparam TaskID User-defined type identifying the concrete task type.
    */
    template<typename TaskID>
    struct stateful_task : public polled_task<TaskID>
    {
        /**
        * @brief Run once when the task is paused.
        *
        * Make the suspended state safe: stop a motor, release a bus, freeze an
        * integrator, save whatever partial progress must not be lost. Pair with
        * `on_resume()`.
        *
        * Pure: if there is nothing to do here, the task did not need this tier.
        */
        virtual void on_pause() = 0;

        /**
        * @brief Run once when a paused task resumes.
        *
        * The mirror of `on_pause()`: re-acquire or restart whatever it released,
        * reinitialize timers, reload cached state.
        *
        * Pure, for the same reason as `on_pause()` - and because a task that
        * releases something on pause and never takes it back is a bug.
        */
        virtual void on_resume() = 0;
    };

} // namespace etask::core

#endif // ETASK_CORE_TASKS_STATEFUL_TASK_HPP_
