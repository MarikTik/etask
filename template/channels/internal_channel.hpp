// SPDX-License-Identifier: BSL-1.1
/**
* @file internal_channel.hpp
*
* @brief Declares the internal communication channel for system-invoked tasks.
*
* The `internal_channel` provides the bridge between tasks that are invoked
* **from within the system itself** (as opposed to external callers) and the
* task manager. Unlike `external_channel`, which serializes results into packets
* for outbound communication, `internal_channel` is intended to deliver results
* back into the system in a local, lightweight manner.
*
* #### Current behavior:
* - `register_task` forwards the task creation request to the global task manager
*   and immediately returns a status code.
* - `on_result` is defined but currently does nothing. In the future, it is
*   intended to capture completed results and deliver them to a placeholder
*   future-like object, allowing synchronous code paths to observe the outcome
*   of internally invoked tasks.
* - `pause_task`, `resume_task`, and `abort_task` forward directly to the global
*   task manager and return immediately with the manager’s status code.
*
* #### Planned extensions:
* A future enhancement will introduce a `track_task` API returning a lightweight,
* single-thread, single-consumer "future-like" object. This will allow callers to
* observe results asynchronously once the `on_result` method is invoked.
*
* @note The current version returns only immediate status codes. Result handling
* is deferred for later iterations of this API.
*
* @see external_channel for handling of results destined to external endpoints.
*
* @date 2025-08-14
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @copyright
* Business Source License 1.1 (BSL 1.1)  
* Copyright (c) 2025 Mark Tikhonov  
* Free for non-commercial use. Commercial use requires a separate license.  
* See LICENSE file for details.
*/
#ifndef CHANNELS_INTENRAL_CHANNEL_HPP_
#define CHANNELS_INTENRAL_CHANNEL_HPP_
#include <etask/system/channel.hpp>
#include <etask/system/status_code.hpp>
#include <etools/memory/envelope.hpp>
#include <etools/memory/envelope_view.hpp>
#include "../global/task_id.hpp"

namespace channels{
    /**
    * @struct internal_channel
    * 
    * @brief Channel implementation for tasks invoked internally by the system.
    *
    * Provides methods for registering, pausing, resuming, and aborting tasks,
    * and will eventually provide a mechanism for collecting results asynchronously.
    *
    * #### Responsibilities:
    * 
    * - Forward task lifecycle commands to the global task manager.
    * 
    * - Act as the origin channel for tasks that are system-initiated.
    * 
    * - Receive task results via `on_result` once tasks complete.
    *
    * #### Limitations (current state):
    * 
    * - `on_result` does not yet forward results anywhere.
    * 
    * - `register_task` cannot provide a future for results, only a status code.
    */
    struct internal_channel : public etask::system::channel<global::task_id>{

        /**
        * @brief Receives a task’s result when invoked by the task manager.
        *
        * @param initiator_id Identifier of the task initiator. For internal tasks,
        *        this is typically reserved or fixed to the system’s ID.
        * @param uid Unique identifier of the task type that completed.
        * @param result The result envelope produced by the task (currently unused).
        * @param code Status code describing the outcome of the task (currently unused).
        *
        * @note This method is currently a placeholder. In the future, it will
        *       populate a future-like object created at task registration.
        */
        void on_result(
            uint8_t initiator_id,
            global::task_id uid,
            etools::memory::envelope<> &&result,
            etask::system::status_code code
        ) override; 

        /**
        * @brief Registers a new task for execution inside the system.
        *
        * Forwards the request to the global task manager. Currently returns only
        * the immediate registration status. In the future, this function will also
        * return a lightweight "future-like" object that becomes ready once the
        * task completes and `on_result` is invoked.
        *
        * @tparam Args Arguments forwarded to the task’s constructor.
        * 
        * @param uid Unique identifier of the task type to instantiate.
        * @param args Arguments forwarded to the task constructor.
        * @return Status code indicating the outcome of registration.
        */
        template<typename... Args>
        [[nodiscard]] etask::system::status_code register_task(global::task_id uid, Args&&...args);

        /**
        * @brief Pauses the specified task if it exists and is currently running.
        * @param uid UID of the task to pause.
        * @return Status code indicating whether the operation succeeded.
        */
        [[nodiscard]] etask::system::status_code pause_task(global::task_id uid);

        /**
        * @brief Resumes the specified task if it exists and is paused.
        * @param uid UID of the task to resume.
        * @return Status code indicating whether the operation succeeded.
        */
        [[nodiscard]] etask::system::status_code resume_task(global::task_id uid);

        /**
        * @brief Aborts the specified task if it exists.
        * @param uid UID of the task to abort.
        * @return Status code indicating whether the operation succeeded.
        */
        [[nodiscard]] etask::system::status_code abort_task(global::task_id uid);
        
        ///@todo in the future add implementation for
        /// [[nodiscard]] shared_future_like<envelope, uint8_t> track_task(global::task_id uid);
        /// that will return a shared future like object  

    };
 
} // namespace channels

#include "internal_channel.tpp"

namespace global{
    /**
    * @brief Global instance of the internal channel, used as the default origin
    * for tasks invoked inside the system.
    */
    inline channels::internal_channel internal_channel;
} // namespace global

#endif //CHANNELS_INTENRAL_CHANNEL_HPP_