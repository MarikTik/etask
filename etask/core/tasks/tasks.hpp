// SPDX-License-Identifier: MIT
/**
* @file tasks.hpp
*
* @brief Module header for the etask task tiers.
*
* @defgroup etask_core_tasks etask::core::tasks
* @ingroup etask_core
*
* A task declares what it *is* by which tier it derives from, and pays for
* exactly that. Each tier adds only the hooks its kind of work actually needs,
* so no task carries a vtable slot for a lifecycle step it does not take.
*
* ## The tiers
*
* | Tier                  | Hooks                                                  | Costs |
* |-----------------------|--------------------------------------------------------|-------|
* | @ref instant_task     | *(none - the constructor is the task)*                 | no vtable, no storage, no tick |
* | @ref task             | `on_complete`                                          | vtable, storage |
* | @ref oneshot_task     | `on_execute`, `on_complete` (`is_finished` sealed true) | + one tick |
* | @ref polled_task      | `on_execute`, `is_finished`, `on_complete`             | + polling |
* | @ref stateful_task    | + `on_pause`, `on_resume`                              | + suspension |
*
* ## Choosing one
*
* - Nothing to say back, nothing to wait for? @ref instant_task. It runs inside
*   the dispatch that delivered it and is gone - no reply, no slot, no dispatch
*   cost. Most of a robot's vocabulary lives here: `stop`, `off`, a setpoint write.
* - Runs once, but the caller wants the answer? @ref oneshot_task. Reading a
*   sensor, running a self-test.
* - Takes several ticks and decides for itself when it is done? @ref polled_task.
* - ...and must be made safe if suspended midway? @ref stateful_task.
*
* Every tier but the first is a managed task: the manager owns it through
* @ref task, drives it across `update()` ticks, and delivers its result through
* a channel. @ref instant_task is a different kind of thing entirely and is run
* by its own manager - see its documentation.
*
* ## No `on_start` anywhere
*
* Setup belongs in the constructor. Tasks are runtime objects created by
* `register_task`, long after every board-level initialization has run, so the
* usual reason for a separate `begin()`-style hook does not apply. A task is
* built with its parameters and its scope context already in hand.
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

#ifndef ETASK_CORE_TASKS_TASKS_HPP_
#define ETASK_CORE_TASKS_TASKS_HPP_
#include "instant_task.hpp"
#include "task.hpp"
#include "oneshot_task.hpp"
#include "polled_task.hpp"
#include "stateful_task.hpp"
#endif // ETASK_CORE_TASKS_TASKS_HPP_
