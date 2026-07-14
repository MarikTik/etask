// SPDX-License-Identifier: BSL-1.1
/**
* @file completion_reason.hpp
*
* @brief Defines the reason a task's `on_complete` was invoked.
*
* @ingroup etask_system etask::system
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
#ifndef ETASK_SYSTEM_COMPLETION_REASON_HPP_
#define ETASK_SYSTEM_COMPLETION_REASON_HPP_
#include <cstdint>

namespace etask::system {
    /**
    * @enum completion_reason
    * @brief System-only, input-only signal telling a task why `on_complete` was invoked.
    *
    * This value never leaves the task: it exists purely for the duration of the
    * `on_complete` call so the override can branch on why it is running. It is
    * never stored, returned, or forwarded to a channel. If a task wants to
    * communicate an outcome to the outside world, that belongs in the `buffer<>`
    * it returns from `on_complete`; the outgoing `status_code` reported via
    * `channel::on_result` (`task_finished`/`task_aborted`) is derived by the
    * task manager from this same reason, independently of the task.
    *
    * @note Codes are partitioned by numeric range, mirroring @ref status_code.
    *       See @ref is_system_reason and @ref is_user_reason.
    */
    enum class completion_reason : std::uint8_t {

        /** @name System-reserved reasons (0x00-0x07) */
        ///@{
        finished = 0x00, /**< is_finished() returned true: natural completion. Framework-only; never pass this to complete_task. */
        aborted  = 0x01, /**< Generic reason for a forced completion; complete_task callers must always supply a reason explicitly. */
        ///@}

        /** @name User-defined reasons (0x08-0xFF) */
        ///@{
        user_defined_start = 0x08 /**< base for caller-supplied reasons passed to complete_task. */
        ///@}
    };

    /**
    * @brief True if the reason belongs to the system-reserved range.
    * @param reason Completion reason to test.
    * @return `true` for 0x00-0x07, otherwise `false`.
    */
    [[nodiscard]] constexpr bool is_system_reason(completion_reason reason) noexcept;

    /**
    * @brief True if the reason belongs to the caller-supplied range.
    * @param reason Completion reason to test.
    * @return `true` for 0x08-0xFF, otherwise `false`.
    */
    [[nodiscard]] constexpr bool is_user_reason(completion_reason reason) noexcept;

} // namespace etask::system
#include "completion_reason.inl"
#endif // ETASK_SYSTEM_COMPLETION_REASON_HPP_
