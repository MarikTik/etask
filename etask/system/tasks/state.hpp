/**
* @file state.hpp
* @brief Declares the `state` class for tracking and managing the execution states of tasks.
*
* @ingroup etask_system_tasks
*
* The `state` class encapsulates a set of bitwise flags to track
* task states during execution, including started, finished, paused,
* and resumed conditions. It provides a fluent interface for state
* transitions, supporting the etask framework’s asynchronous
* and interruptible task lifecycle.
*
* Typical usage is within a task class to decide control flow
* or support lifecycle orchestration by a task manager.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-03 - Added Basic State Management
*
* @date 2025-07-09 - Added Aborted State and `noexcept` specifiers to all methods
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_SYSTEM_TASKS_STATE_HPP_
#define ETASK_SYSTEM_TASKS_STATE_HPP_
#include <cstdint>

namespace etask::system::tasks {
    
    /**
    * @class state
    * @brief Represents and manipulates the state of a task using bit flags.
    *
    * The `state` class allows querying and updating a task's status
    * via a set of predefined flags. Each flag represents a possible
    * task state such as started, finished, cancelled, or halted.
    * This supports flexible and performant state transitions in
    * systems where tasks may be paused, resumed, interrupted,
    * or completed asynchronously.
    *
    * @note All methods modifying the state return a reference
    *       to enable fluent-style chaining.
    */
    class state {
    private:
        /**
        * @enum state_flags
        * @brief Enumeration defining task state flags.
        *
        * Each state is encoded as a bit value to allow efficient
        * combination and testing via bitwise operators.
        */
        enum state_flags : std::uint8_t {
            idle      = 1 << 0, /**< Task is idle (not started). */
            started   = 1 << 1, /**< Task has begun execution. */
            finished  = 1 << 2, /**< Task has completed execution. */
            paused    = 1 << 3, /**< Task execution is paused or paused. */
            resumed   = 1 << 4, /**< Task has resumed execution after being paused. */
            aborted   = 1 << 5, /**< Task has been aborted/cancelled. */
            running   = 1 << 6  /**< Task is currently running (started but not finished). */
        };
    public:
        /** @name Query Methods */
        ///@{
        /**
        * @brief Checks if the task has started.
        * @return True if the task has started; false otherwise.
        */
        inline bool is_started() const noexcept;
        
        /**
        * @brief Checks if the task is finished.
        * @return True if the task is finished; false otherwise.
        */
        inline bool is_finished() const noexcept;

        /**
        * @brief Checks if the task is halted.
        * @return True if the task is halted; false otherwise.
        */
        inline bool is_paused() const noexcept;

        /**
        * @brief Checks if the task is resumed after being paused.
        * @return True if the task is resumed; false otherwise.
        */
        inline bool is_resumed() const noexcept;

        /**
        * @brief Checks if the task is aborted.
        * @return True if the task is aborted; false otherwise.
        * */
        inline bool is_aborted() const noexcept;

        /**
        *  
        * @brief Checks if the task is currently running.
        * @return True if the task is running; false otherwise.
        */
        inline bool is_running() const noexcept;

        /**
        * @brief Checks if the task is idle (not running).
        * @return True if the task is idle; false otherwise.
        */
        inline bool is_idle() const noexcept;
        ///@}
        
        /** @name State Modification Methods */
        ///@{
        
        /**
        * @brief Sets the `paused` flag, and maintains proper state.
        * 
        * - sets the `paused` flag.
        * 
        * - sets the `idle` flag.
        * 
        * - clears the `running` flag.
        * 
        * - clears the `resumed` flag.
        * 
        * @return Reference to the updated `state` object.
        */
        inline state& set_paused() noexcept;  
        
        /**
        * @brief Sets the resumed flag and maintains proper state.
        * 
        * - sets the `resumed` flag.
        * 
        * - sets the `running` flag.
        * 
        * - clears the `pause` flag.
        * 
        * - clears the `idle` flag. 
        * 
        * @return Reference to the updated `state` object.
        */
        inline state& set_resumed() noexcept;
        
        /**
        * @brief Marks the task as started.
        * @return Reference to the updated `state` object.
        */
        inline state& set_started() noexcept;
        
        /**
        * @brief Sets the finished state flag.
        * @return Reference to the updated `state` object.
        */
        inline state& set_finished() noexcept;

        /**
        * @brief Marks the task as aborted.
        * @return Reference to the updated `state` object.
        */
        inline state& set_aborted() noexcept;

        /**
        * @brief Marks the task as running, clearing the idle state.
        * @return Reference to the updated `state` object.
        */
        inline state& set_running() noexcept;

        /**
        * @brief Marks the task as idle, clearing the running state.
        * @return Reference to the updated `state` object.
        */
        inline state& set_idle() noexcept;
        ///@}
    private:
        state_flags _state = state_flags::running; /**< Internal bitmask representing current task state. */
    };
    
} // namespace etask::system::tasks
#include "state.inl"
#endif // ETASK_SYSTEM_TASKS_STATE_HPP_
