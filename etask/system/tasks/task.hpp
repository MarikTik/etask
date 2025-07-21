/**
* @file task.hpp
*
* @brief Defines the abstract base class for tasks in the etask framework.
*
* @ingroup etask_system_tasks
*
* This file declares the `etask::system::tasks::task` class template,
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
* - return an empty envelope and status code `0` in `on_complete()`
*
* ## Task Identification
*
* Each task type is identified by a user-defined TaskID value (often
* an enum or other bit-encoded type). This enables precise routing
* of tasks in the task manager.
*
* Example:
* @code
* using e_task = etask::system::tasks::task<UID_t>;
*
* class move_task : public e_task {
* public:
*     static constexpr UID_t uid = 0x01;
*
*     move_task(etask::system::tools::envelope_view env) {
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
*     std::pair<etask::system::tools::envelope, std::uint8_t>
*     on_complete(bool interrupted) override {
*         // return result and status code
*         return {etask::system::tools::envelope{}, 0};
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
*/

#ifndef ETASK_SYSTEM_TASKS_TASK_HPP_
#define ETASK_SYSTEM_TASKS_TASK_HPP_
#include <cstdint>
#include <utility>
#include "../tools/envelope.hpp"

namespace etask::system::tasks {
    
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
    * - `on_complete(bool interrupted)`  
    *   Called once at the end of the task lifecycle, either after
    *   normal completion or after forced termination.
    *
    * ## Default Implementations
    *
    * All lifecycle methods except `is_finished()` and
    * `on_complete()` provide default empty implementations.
    *
    * - `is_finished()` returns `true` by default, meaning the task
    *   completes immediately unless overridden.
    *
    * - `on_complete()` returns an empty envelope and status code `0`
    *   by default, indicating no result data and no error.
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
        * - after forced termination by external command.
        *
        * Override this method to finalize the task, clean up resources,
        * and return any results as a serialized envelope.
        *
        * @param interrupted `true` if the task was forcibly terminated
        *                    before natural completion; otherwise `false`.
        *
        * @return A pair containing:
        * - an `etask::system::tools::envelope` with any result data
        * - a `std::uint8_t` status code defined by the user to indicate
        *   success, failure, or custom task-specific outcomes
        *
        * The base implementation returns an empty envelope and
        * status code `0`.
        */
        virtual std::pair<tools::envelope, std::uint8_t> on_complete(bool interrupted);
        
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
    
} // namespace etask::system::tasks

#include "task.tpp"
#endif // ETASK_SYSTEM_TASKS_TASK_HPP_
