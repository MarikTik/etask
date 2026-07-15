// SPDX-License-Identifier: BSL-1.1
/**
* @file task.hpp
*
* @brief Defines the abstract base class for tasks in the etask framework.
*
* @ingroup etask_system etask::system
*
* This file declares the `etask::system::task` class template,
* which provides the standard interface and lifecycle hooks for implementing
* task-oriented architectures in the etask framework.
*
* Tasks encapsulate discrete units of work to be scheduled and controlled
* by a task manager. They are primarily designed for embedded platforms
* such as the ESP series, but are generic enough to support any C++17-capable
* target.
*
* ## Framework Integration
*
* The methods in this class are **never called directly by user code**.
* Instead, they serve as **callback hooks** that the etask framework
* invokes at specific points in the task's lifecycle. Users derive
* from this class and override whichever methods are relevant for
* their task's logic.
*
* The default implementations:
* - perform no operations for all lifecycle methods
* - immediately consider the task finished (`is_finished` returns `true`)
* - return an empty result buffer in `on_complete()`
*
* ## Task Identification
*
* Each task type is identified by a user-defined TaskID value (often
* an enum or other bit-encoded type). This enables precise routing
* of tasks in the task manager.
*
* Example:
* @code
* using e_task = etask::system::task<UID_t>;
*
* class move_task : public e_task {
* public:
*     static constexpr UID_t uid = 0x01;
*
*     move_task(etools::memory::buffer_view env) {
*         // extract parameters from env if needed
*     }
*
*     void on_start() override {
*         // perform initialization
*     }
*
*     void on_execute() override {
*         // execute one iteration
*     }
*
*     bool is_finished() override {
*         // decide when work is done
*         return true;
*     }
*
*     etools::memory::buffer<> on_complete(etask::system::completion_reason reason) override {
*         // reason tells you *why* (finished naturally vs. forced completion);
*         // it is not part of the result. Return whatever data you want the
*         // caller to receive.
*         return etools::memory::buffer<>{};
*     }
* };
* @endcode

* @author
* Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-03
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*
* @par Changelog
* - 2025-07-03
*      - Initial creation.
* - 2025-07-20
*      - Modified example code to use `etask::system::tools::envelope_view` in task construction.
* - 2026-07-13
*      - on_complete now takes a completion_reason and returns etools::memory::buffer<>
*        instead of bool interrupted and a std::pair<envelope<>, uint8_t>.
*/

#ifndef ETASK_SYSTEM_TASK_HPP_
#define ETASK_SYSTEM_TASK_HPP_
#include <cstdint>
#include <utility>
#include <etools/memory/buffer.hpp>
#include "completion_reason.hpp"

namespace etask::system {
    
    /**
    * @class task
    * @brief Abstract base class for tasks managed by the etask framework.
    *
    * The `task` class defines the contract for all tasks integrated into
    * the etask framework. Each task represents a discrete operation,
    * which can be started, paused, resumed, executed incrementally,
    * and ultimately completed, either normally or in response to
    * external termination.
    *
    * **Important:** These methods are not called directly by user code.
    * They are called exclusively by the framework's task manager.
    *
    * ## Lifecycle Hooks
    *
    * - `on_start()`  
    *   Called exactly once when the task begins.
    *
    * - `on_execute()`  
    *   Called repeatedly while the task is running, until
    *   `is_finished()` returns true or external control
    *   intervenes.
    *
    * - `on_pause()`  
    *   Called if the task is paused by external command.
    *
    * - `on_resume()`  
    *   Called if the task resumes after being paused.
    *
    * - `on_complete(completion_reason reason)`
    *   Called once at the end of the task lifecycle, either after
    *   normal completion or after forced termination. `reason` is
    *   system-only and input-only: see @ref completion_reason.
    *
    * ## Default Implementations
    *
    * All lifecycle methods except `is_finished()` and
    * `on_complete()` provide default empty implementations.
    *
    * - `is_finished()` returns `true` by default, meaning the task
    *   completes immediately unless overridden.
    *
    * - `on_complete()` returns an empty result buffer by default.
    *
    * @tparam TaskID User-defined type (commonly an enum or bitfield type)
    *         identifying this specific task type. Enables the task manager
    *         to differentiate between various task implementations.
    */
    template<typename TaskID>
    struct task
    {
        /**
        * @brief Called by the framework to initialize the task.
        *
        * This method executes once before the first call to `on_execute()`.
        * Override this method to perform any setup logic, such as
        * parameter validation or hardware initialization.
        *
        * The base implementation performs no operations.
        */
        virtual void on_start();
        
        /**
        * @brief Called repeatedly while the task is running.
        *
        * The framework calls this method in a loop until either:
        * - `is_finished()` returns true, or
        * - the task is halted or terminated by external command.
        *
        * Override this method to implement the task's incremental
        * execution logic.
        *
        * The base implementation performs no operations.
        */
        virtual void on_execute();
        
        /**
        * @brief Checks whether the task has finished its work.
        *
        * The framework calls this after each `on_execute()` cycle to
        * decide whether to continue the task.
        *
        * Override this method to define your own completion condition.
        *
        * @return `true` if the task has finished and should proceed
        *         to completion; `false` if it should continue executing.
        *
        * The base implementation always returns `true`, causing
        * the task to finish immediately unless overridden.
        */
        virtual bool is_finished();
        
        /**
        * @brief Called by the framework when the task completes.
        *
        * This method is called exactly once, either:
        * - after normal completion (when `is_finished()` returns true), or
        * - after forced termination via `task_manager::complete_task`.
        *
        * Override this method to finalize the task, clean up resources,
        * and return any results as a serialized buffer.
        *
        * @param reason Why `on_complete` is being invoked. A system-only,
        *               input-only value that exists purely for this call:
        *               it is never stored, returned, or forwarded anywhere.
        *               `completion_reason::finished` for natural completion;
        *               `completion_reason::aborted` or a caller-supplied
        *               reason for a forced completion. See @ref completion_reason.
        *
        * @return An `etools::memory::buffer` with any result data. Users are not
        *         required to signal success/failure here; any application-level
        *         outcome can be encoded into the returned buffer if desired.
        *
        * The base implementation returns an empty buffer.
        */
        virtual etools::memory::buffer<> on_complete([[maybe_unused]] completion_reason reason);
        
        /**
        * @brief Called by the framework when the task is paused.
        *
        * This method is triggered if the framework decides to pause
        * the task during execution (e.g., due to external control signals).
        *
        * Override this method to:
        * - stop hardware safely
        * - save partial state
        * - ensure the task can later resume properly
        *
        * The base implementation performs no operations.
        */
        virtual void on_pause();
        
        /**
        * @brief Called by the framework when the task is resumed after being paused.
        *
        * This method is triggered if the task resumes operation
        * after a pause.
        *
        * Override this method to:
        * - restore hardware state
        * - reinitialize timers
        * - reload cached data or parameters
        *
        * The base implementation performs no operations.
        */
        virtual void on_resume();
        
        /**
        * @brief Virtual destructor for proper cleanup via base pointers.
        */
        virtual ~task() = default;
    };
    
} // namespace etask::system

#include "task.tpp"
#endif // ETASK_SYSTEM_TASK_HPP_
