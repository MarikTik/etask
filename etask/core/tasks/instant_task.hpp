// SPDX-License-Identifier: MIT
/**
* @file instant_task.hpp
*
* @brief Declares `etask::core::instant_task`, a fire-and-forget command that
*        runs to completion the moment it arrives.
*
* @ingroup etask_core etask::core::tasks
*
* ## What an instant task is
*
* An instant task is a **command**, not a managed task. It arrives, it runs, it
* is gone - all inside the dispatch that delivered it. It never enters the
* manager's storage, never sees an `update()` tick, and never produces a reply.
*
* That is not a degenerate task: it is what most of a robot's vocabulary
* actually looks like. `stop`, `off`, `reboot`, a setpoint write - none of them
* have anything to say back, and none of them need to exist for longer than the
* call that triggers them.
*
* ## What it costs: nothing
*
* `instant_task` declares **no virtual functions at all**, so a derived command
* has no vtable and no vptr. It is constructed on the stack by
* @ref instant_task_manager, run, and destroyed - so it also occupies no
* registry slot, no `_tasks` entry, and no garbage bit. A project built entirely
* out of instant tasks performs no virtual dispatch anywhere in the task layer.
*
* It is deliberately **not** derived from @ref task: joining that hierarchy
* would mean inheriting a vtable for an `on_complete` it does not have.
*
* ## The contract
*
* A derived command supplies:
*
* - a constructor taking its schema parameters (and its scope `context&`, if it
*   is in a scope) - this is where the work happens, or is launched from;
* - a `static constexpr TaskID uid`.
*
* There are no lifecycle hooks to override, because there is no lifecycle.
*
* @code
* class stop : public etask::core::instant_task {
* public:
*     static constexpr global::task_id uid = global::task_id::rotors_fl_stop;
*
*     explicit stop(context& ctx) {
*         ctx.motor.cut();   // done. no reply, no tick, no storage.
*     }
* };
* @endcode
*
* ## Consequences to be aware of
*
* - **No reply reaches the requester** - not even a success status. A caller
*   that needs confirmation wants a @ref oneshot_task instead.
* - **It cannot be paused, resumed, or completed.** There is no instance to
*   address: by the time any directive could arrive, the command has already
*   run and been destroyed. Such a directive is answered with
*   `status_code::task_not_addressable`.
* - **It runs in the caller's context**, i.e. inside whatever context delivered
*   the packet, which on an asynchronous transport may be a callback. Keep the
*   body short and non-blocking, exactly as the name promises.
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

#ifndef ETASK_CORE_TASKS_INSTANT_TASK_HPP_
#define ETASK_CORE_TASKS_INSTANT_TASK_HPP_

namespace etask::core {

    /**
    * @class instant_task
    *
    * @brief Tag base for a fire-and-forget command. Adds no members, no
    *        virtuals, and no size.
    *
    * Deriving from this marks a class as an instant command: it is what the
    * generator keys its tier on, what @ref instant_task_manager accepts, and
    * what tells a reader that the constructor *is* the whole task. It is an
    * empty base, so a derived command is exactly as large as its own members.
    *
    * @note Not a class template. There is no `TaskID` parameter because there is
    *       nothing here to parameterize: no virtual to dispatch, no base pointer
    *       to own the task through. A command's `uid` is a `static constexpr`
    *       member of the derived class, which is where the manager reads it from.
    */
    struct instant_task {
        
    };

} // namespace etask::core

#endif // ETASK_CORE_TASKS_INSTANT_TASK_HPP_
