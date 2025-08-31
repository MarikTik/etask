// SPDX-License-Identifier: BSL-1.1
/**
* @file status_code.hpp
*
* @brief Defines the status codes used by the etask system for task execution reporting and error handling.
*
* @ingroup etask_system etask::system
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
#ifndef ETASK_SYSTEM_STATUS_CODE_HPP_
#define ETASK_SYSTEM_STATUS_CODE_HPP_
#include <cstdint>

namespace etask::system{
    /**
    * @enum status_code
    * @brief Unified status space used in packets and API returns.
    *
    * @note Codes are partitioned by numeric range for readability and fast checks.
    *       See @ref is_manager_status and @ref is_task_status.
    */
    enum status_code : std::uint8_t {

        /** @name Manager/API status codes (0x00–0x1F) */
        ///@{
        ok                      = 0x00, /**< General success. */
        task_not_registered     = 0x01, /**< Operated on a task that is not registered. */
        task_already_running    = 0x02, /**< Start/resume requested but task is already running. */
        task_already_paused     = 0x03, /**< Pause requested but task is already paused. */
        task_already_resumed    = 0x04, /**< Resume requested but task already marked resumed. */
        task_not_paused         = 0x05, /**< Resume requested but task is not paused. */
        task_not_running        = 0x06, /**< Pause requested but task is not running. */
        invalid_state_transition= 0x07, /**< Illegal state change for current task state. */
        task_already_finished   = 0x08, /**< Operation invalid: task already finished. */
        task_already_aborted    = 0x09, /**< Operation invalid: task already aborted. */

        permission_denied       = 0x0A, /**< Initiator not authorized for this operation. */
        would_block             = 0x0B, /**< Unsafe/forbidden in current context (e.g., ISR). */
        reentrancy_conflict     = 0x0C, /**< Manager API called while update() is active. */

        channel_null            = 0x0D, /**< Null channel pointer provided. */
        channel_error           = 0x0E, /**< Channel failed/backpressure (if detectable). */

        constructor_not_found   = 0x0F, /**< Registry has UID but no constructible entry/signature mismatch. */
        invalid_params          = 0x10, /**< Envelope invalid/unsupported for this task type. */
        out_of_memory           = 0x11, /**< Allocation failure when constructing task. */
        task_limit_reached      = 0x12, /**< Manager concurrency cap reached. */
        duplicate_task          = 0x13, /**< Duplicate instance disallowed by policy. */
        task_unknown            = 0x14, /**< Task type UID is unknown to the registry. */

        internal_error          = 0x1F, /**< Unexpected manager fault. */
        ///@}

        /** @name Task/runtime status codes (0x20–0x3F) */
        ///@{
        task_finished           = 0x20, /**< Task completed successfully (normal termination). */
        task_aborted            = 0x21, /**< Task terminated early by abort request. */

        task_timeout            = 0x22, /**< Task exceeded its time budget/deadline. */
        task_io_error           = 0x23, /**< Task I/O/subsystem failure. */
        task_validation_failed  = 0x24, /**< Task rejected inputs/parameters at runtime. */
        task_dependency_missing = 0x25, /**< Dependency/service required by task unavailable. */
        task_busy               = 0x26, /**< Task refused action due to its own constraints. */
        ///@}

        /** @name Custom/user-defined status codes (0x70–0xFF) */
        ///@{
        custom_error_start      = 0x70  /**< base for user extensions. */
        ///@}
    };

    /**
    * @brief True if the code belongs to the manager/API range.
    * @param code Status code to test.
    * @return `true` for 0x00–0x1F, otherwise `false`.
    */
    [[nodiscard]] constexpr bool is_manager_status(status_code code) noexcept;

    /**
    * @brief True if the code belongs to the task/runtime range.
    * @param code Status code to test.
    * @return `true` for 0x20–(custom_error_start-1), otherwise `false`.
    */
    [[nodiscard]] constexpr bool is_task_status(status_code code) noexcept;

    /**
    * @brief True if the code belongs to the custom range.
    * @param code Status code to test.
    * @return `true` for 0x70 (custom_error_start-1) - 0xFF, otherwise `false`.
    */
    [[nodiscard]] constexpr bool is_custom_status(status_code code) noexcept;
} // namespace etask::system
#include "status_code.inl"
#endif // ETASK_SYSTEM_STATUS_CODE_HPP_
 