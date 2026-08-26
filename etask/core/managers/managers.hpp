// SPDX-License-Identifier: MIT
/**
* @file managers.hpp
*
* @brief Module header for the etask task managers.
*
* @defgroup etask_core_managers etask::core::managers
* @ingroup etask_core
*
* Each task tier has genuinely different machinery behind it, so each gets its
* own manager rather than one manager carrying branches most tasks never take:
*
* | Manager                     | Owns                 | Storage | Per-tick work |
* |-----------------------------|----------------------|---------|---------------|
* | @ref instant_task_manager   | @ref instant_task    | none    | none          |
* | @ref polled_task_manager    | @ref polled_task     | slots   | execute, poll |
* | @ref stateful_task_manager  | @ref stateful_task   | slots   | + suspension  |
*
* @ref task_manager composes all three and is the only one an application names.
* It routes each call to the tier that owns the uid - a compile-time decision -
* and a tier with no tasks is never instantiated, so its storage and code do not
* exist in the binary at all.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-25
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_MANAGERS_MANAGERS_HPP_
#define ETASK_CORE_MANAGERS_MANAGERS_HPP_
#include "instant_task_manager.hpp"
#include "polled_task_manager.hpp"
#include "stateful_task_manager.hpp"
#include "task_manager.hpp"
#endif // ETASK_CORE_MANAGERS_MANAGERS_HPP_
