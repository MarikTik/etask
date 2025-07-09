/**
* @file channel.hpp
*
* @brief Declares the communication channel interface for task result handling in the etask framework.
*
* @ingroup etask_system_management etask::system::management
*
* Defines the core communication mechanism for propagating task results
* and statuses within the etask framework.
*
* The purpose of the `channel` class is to decouple the execution of tasks from the delivery
* and handling of their results. This separation enables a flexible and modular architecture
* where different components (such as task managers, message routers, or external services)
* can handle task outcomes without direct knowledge of the task implementation.
*
* The `channel` interface is purely abstract, requiring the implementation of the `on_result`
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
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_SYSTEM_MANAGMENT_CHANNEL_HPP_
#define ETASK_SYSTEM_MANAGMENT_CHANNEL_HPP_

#include "../tools/envelope.hpp"
#include "../system/status_code.hpp"

namespace etask::system::management {
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
    * The communication is performed via the `on_result` method, which delivers:
    * - A result payload encapsulated in a `tools::envelope` object.
    * - A `status_code` indicating the outcome of the task, such as success, error, or cancellation.
    *
    * Derived classes must implement this method to define the desired result-handling behavior.
    */
    struct channel {
        /**
        * @brief Receives the result of a task execution.
        *
        * This method is called by the task manager whenever a task finishes, either normally
        * or due to interruption, abortion, or error. It provides a mechanism for passing
        * task results and associated status codes to the external environment.
        *
        * @param result
        *        An envelope containing the result data produced by the task.
        *
        * @param code
        *        A status code describing the outcome of the task, such as success,
        *        and specific errors.
        *
        * @note
        * - Must be implemented by any derived class.
        * - The channel mechanism is designed to remain agnostic of the specific task
        *   logic, ensuring a clean separation of concerns.
        */
        virtual void on_result(const tools::envelope result, status_code code) = 0;
    };
    
} // namespace etask::system::management

#endif // ETASK_SYSTEM_MANAGMENT_CHANNEL_HPP_
