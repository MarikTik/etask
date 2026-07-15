// SPDX-License-Identifier: BSL-1.1
/**
* @file internal_channel.hpp
*
* @brief Declares the internal communication channel for system-invoked tasks.
*
* @ingroup etask_core etask::core
*
* The `internal_channel` provides the bridge between tasks that are invoked
* **from within the system itself** (as opposed to external callers arriving
* over the wire) and a `task_manager`. Unlike an external channel, which
* serializes results into packets for outbound communication, `internal_channel`
* delivers results back into the system in a local, lightweight manner.
*
* ## Dependency injection
*
* This is core library mechanism, not application code: it is parameterized on
* the concrete `Manager` type (a `task_manager<...>` instantiation) rather than
* reaching for a global name by convention. A user project constructs exactly
* one `internal_channel<Manager>`, bound by reference to its one `Manager`
* instance, in its composition root.
*
* `Manager` supplies `task_uid_t` and `channel_t` (both public on `task_manager`)
* and the register/pause/resume/complete API this channel forwards to. The
* generated task uid enum is never named directly here - it arrives
* transitively as `Manager::task_uid_t`.
*
* This device's own identity - used as `initiator_id` when a task on this
* device starts another task - is **not** a parameter of this class at all.
* It is `ECOMM_BOARD_ID` (`<ecomm/protocol/config.hpp>`): a single,
* project-wide, range-checked compile-time constant that already exists for
* exactly this purpose at the communication layer. There is one "who am I"
* per firmware build, not one per channel; sourcing it from `ecomm` instead
* of re-deriving a parallel etask-local identity keeps that invariant true
* by construction.
*
* #### Current behavior:
* - `register_task`/`pause_task`/`resume_task`/`complete_task` forward directly
*   to the injected `Manager` and return immediately with its status code.
* - `on_result` is defined but currently does nothing. In the future, it is
*   intended to capture completed results and deliver them to a placeholder
*   future-like object, allowing synchronous code paths to observe the outcome
*   of internally invoked tasks.
*
* #### Planned extensions:
* A future enhancement will introduce a `track_task` API returning a lightweight,
* single-thread, single-consumer "future-like" object. This will allow callers to
* observe results asynchronously once `on_result` is invoked.
*
* @note The current version returns only immediate status codes. Result handling
*       is deferred for later iterations of this API.
*
* @see channel for the abstract result-delivery interface this implements.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-07-13
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_INTERNAL_CHANNEL_HPP_
#define ETASK_CORE_INTERNAL_CHANNEL_HPP_
#include "channel.hpp"
#include "status_code.hpp"
#include "completion_reason.hpp"
#include <etools/memory/buffer.hpp>
#include <ecomm/protocol/config.hpp>
#include <cstdint>

namespace etask::core {

    /**
    * @class internal_channel
    *
    * @brief Channel implementation for tasks invoked internally by the system.
    *
    * @tparam Manager A `task_manager<...>` instantiation. Injected by reference
    *         at construction; not owned. Must outlive this channel.
    *
    * #### Responsibilities:
    *
    * - Forward task lifecycle commands to the injected task manager.
    * - Act as the origin channel for tasks that are system-initiated.
    * - Receive task results via `on_result` once tasks complete.
    *
    * #### Limitations (current state):
    *
    * - `on_result` does not yet forward results anywhere.
    * - `register_task` cannot provide a future for results, only a status code.
    */
    template<typename Manager>
    class internal_channel : public channel<typename Manager::task_uid_t> {
    public:
        /** @typedef task_uid_t
        * @brief The task identifier type, taken from `Manager::task_uid_t`.
        */
        using task_uid_t = typename Manager::task_uid_t;

        /**
        * @brief Binds this channel to the manager it forwards to.
        * @param manager The task manager this channel drives. Must outlive
        *        this channel; held by reference, not owned.
        */
        explicit internal_channel(Manager& manager) noexcept;

        /// @brief Deleted copy constructor - an adapter bound to one manager instance.
        internal_channel(const internal_channel&) = delete;
        /// @brief Deleted copy assignment - see the deleted copy constructor.
        internal_channel& operator=(const internal_channel&) = delete;
        /// @brief Deleted move constructor - see the deleted copy constructor.
        internal_channel(internal_channel&&) = delete;
        /// @brief Deleted move assignment - see the deleted copy constructor.
        internal_channel& operator=(internal_channel&&) = delete;

        /**
        * @brief Receives a task's result when invoked by the task manager.
        *
        * @param initiator_id Identifier of the task initiator. For internal
        *        tasks, this is `ECOMM_BOARD_ID` - this device's own id.
        * @param uid Unique identifier of the task type that completed.
        * @param result The result buffer produced by the task (currently unused).
        * @param code Status code describing the outcome of the task (currently unused).
        *
        * @note This method is currently a placeholder. In the future, it will
        *       populate a future-like object created at task registration.
        */
        void on_result(
            std::uint8_t initiator_id,
            task_uid_t uid,
            etools::memory::buffer<>&& result,
            status_code code
        ) override;

        /**
        * @brief Registers a new task for execution inside the system.
        *
        * Forwards the request to the injected task manager, using
        * `ECOMM_BOARD_ID` as the initiator. Currently returns only the
        * immediate registration status. In the future, this function will
        * also return a lightweight "future-like" object that becomes ready
        * once the task completes and `on_result` is invoked.
        *
        * @tparam Args Arguments forwarded to the task's constructor.
        *
        * @param uid Unique identifier of the task type to instantiate.
        * @param args Arguments forwarded to the task constructor.
        * @return Status code indicating the outcome of registration.
        */
        template<typename... Args>
        [[nodiscard]] status_code register_task(task_uid_t uid, Args&&... args);

        /**
        * @brief Pauses the specified task if it exists and is currently running.
        * @param uid UID of the task to pause.
        * @return Status code indicating whether the operation succeeded.
        */
        [[nodiscard]] status_code pause_task(task_uid_t uid);

        /**
        * @brief Resumes the specified task if it exists and is paused.
        * @param uid UID of the task to resume.
        * @return Status code indicating whether the operation succeeded.
        */
        [[nodiscard]] status_code resume_task(task_uid_t uid);

        /**
        * @brief Forces the specified task to complete before it would on its own.
        * @param uid UID of the task to complete.
        * @param reason Why the task is being force-completed. See
        *        `task_manager::complete_task` - there is no default; callers
        *        must always be explicit.
        * @return Status code indicating whether the operation succeeded.
        */
        [[nodiscard]] status_code complete_task(task_uid_t uid, completion_reason reason);

        ///@todo in the future add implementation for
        /// [[nodiscard]] shared_future_like<buffer<>, status_code> track_task(task_uid_t uid);
        /// that will return a shared future like object so that on_result can update it

    private:
        Manager& _manager;
    };

} // namespace etask::core

#include "internal_channel.tpp"
#endif // ETASK_CORE_INTERNAL_CHANNEL_HPP_
