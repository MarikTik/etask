#ifndef SYSTEM_TASKS_HPP_
#define SYSTEM_TASKS_HPP_
/**
* @file tasks.hpp
* @brief Entry point for the etask system tasks module.
*
* This header aggregates all components related to task management
* in the etask framework. It provides unified inclusion of task
* classes and utilities, simplifying usage and integration.
*
* Including this file provides access to:
* - `etask::system::tasks::task` — the base interface for defining asynchronous tasks.
* - `etask::system::tasks::state` — a utility class for managing task states.
*
* @brief Task-related classes and utilities for the etask framework.
*
* @defgroup etask_system_tasks etask::system::tasks
* This module contains fundamental building blocks for task-oriented
* development in the etask framework. It covers task lifecycle
* management, state handling, and related utilities to enable
* reliable task-driven architectures, especially for embedded systems
* like ESP microcontrollers.
*
* Typical usage:
* @code{.cpp}
* #include "system/tasks/tasks.hpp"
*
* class my_task : public etask::system::tasks::task<MyTaskID> {
* public:
*     void on_start() override {
*         // Initialization code
*     }
* };
* @endcode
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-03
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/

/// @addtogroup etask_system_tasks
/// @{
#include "task.hpp"
#include "state.hpp"
/// @}

#endif // SYSTEM_TASKS_HPP_
