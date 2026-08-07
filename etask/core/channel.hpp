// SPDX-License-Identifier: MIT
/**
* @file channel.hpp
*
* @brief Declares the communication channel interface for task result handling in the etask framework.
*
* @ingroup etask_core etask::core
*
* Defines the core communication mechanism for propagating task results
* and statuses within the etask framework.
*
* The purpose of the `channel` class is to decouple the execution of tasks from the delivery
* and handling of their results. This separation enables a flexible and modular architecture
* where different components (such as task managers, message routers, or external services)
* can handle task outcomes without direct knowledge of the task implementation.
*
* The `channel` interface is purely abstract, requiring the implementation of the `complete`
* method in derived classes.
*
* ### Responsibilities of channel
*
* - Receive results and status codes emitted by tasks.
* - Provide a unified interface for delivering results to diverse endpoints.
* - Decouple task logic from result handling logic.
* - Enable pluggable implementations for different communication backends.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-09
*
* @copyright
* MIT License
* Copyright (c) 2025 Mark Tikhonov
* See LICENSE file for details.
* @par Changelog
* - 2025-07-03 
*      - Initial creation.
* - 2025-07-15
*      - Parametrized the channel with `TaskID_t` to allow proper creation of packets.
* - 2025-07-20
*      - Added `initiator_id` parameter to `on_result` method to allow proper routing of results.
*      - Changed type of `result` parameter to `tools::envelope &&` to allow move semantics.
*/
#ifndef ETASK_CORE_CHANNEL_HPP_
#define ETASK_CORE_CHANNEL_HPP_
#include "status_code.hpp"
#include "completion_reason.hpp"
#include "task.hpp"
#include <cstdint>
namespace etask::core {
    /**
    * @struct channel
    *
    * @brief Abstract interface representing a communication channel for task result delivery.
    *
    * The `channel` class defines the contract for any entity that wishes to
    * receive notifications of task outcomes within the etask framework. It acts as a
    * bridge between task execution logic and external systems or subsystems interested
    * in the results of asynchronous task operations.
    *
    * Implementations of this interface handle how task results are propagated or processed,
    * whether that means storing results locally, sending them over a network, logging them,
    * or triggering further actions in the system.
    *
    * Each task managed by the `task_manager` is associated with a specific `channel` instance,
    * ensuring that results are routed correctly and independently of other tasks running
    * in the system.
    *
    * The manager hands a concluding task to its channel via the `complete` method.
    * The channel owns the result destination (an outgoing packet's payload, or a
    * discard scratch), so it - not the manager - drives `on_complete`: it
    * designates the region, invokes the task, and disposes of the result. A task's
    * returned @ref outcome lands in that region with no heap and no copy (see
    * @ref detail::result_region).
    *
    * Derived classes must implement this method to define the desired result-handling behavior.
    * 
    * @tparam TaskID The underlying type used for task identifiers (e.g. uint8_t, uint16_t).
    */
    template<typename TaskID_t>
    struct channel {
        /**
        * @brief Concludes a task and disposes of its result.
        *
        * Called by the task manager when a task finishes, either normally or due
        * to interruption, abortion, or error. The channel designates the result
        * region, calls `t.on_complete(reason)` (which packs the task's returned
        * @ref outcome straight into that region), then disposes of the result: an
        * external channel seals and sends the packet; an internal channel discards it.
        *
        * @param initiator_id The id of the device or component that initiated the task.
        * @param task_id       The unique identifier of the concluding task.
        * @param code          Status describing the outcome (e.g. `task_finished`,
        *                       `task_aborted`).
        * @param reason         Why the task is concluding; forwarded to `on_complete`.
        *                       Input-only, never stored.
        * @param t              The concluding task, invoked through its base to
        *                       produce the result in place.
        *
        * @note
        * - Must be implemented by any derived class.
        * - The channel mechanism is designed to remain agnostic of the specific task
        *   logic, ensuring a clean separation of concerns.
        */
        virtual void complete(
            uint8_t initiator_id,
            TaskID_t task_id,
            status_code code,
            completion_reason reason,
            task<TaskID_t>& t
        ) = 0;
    };
    
} // namespace etask::core

#endif // ETASK_CORE_CHANNEL_HPP_
