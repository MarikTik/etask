// SPDX-License-Identifier: BSL-1.1
/**
* @file completion_reason.hpp
*
* @brief Defines the reason a task's `on_complete` was invoked.
*
* @ingroup etask_core etask::core
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
#ifndef ETASK_CORE_COMPLETION_REASON_HPP_
#define ETASK_CORE_COMPLETION_REASON_HPP_
#include <cstdint>

namespace etask::core {
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
    *
    * @note Constrained to **6 bits** (valid range `[0, max]`, `max = 0x3F`), not
    *       the full range of the `uint8_t` backing this enum. `external_channel`
    *       packs `wire_command` (2 bits) and `completion_reason` (6 bits) into a
    *       single wire byte - see `channels/wire_command.hpp`. Rather than have
    *       that packing silently truncate/corrupt an out-of-range reason, the
    *       6-bit ceiling is the type's canonical range everywhere, enforced by
    *       `task_manager::complete_task` (see @ref is_valid_reason) regardless of
    *       whether the caller is on-wire or in-process.
    */
    enum class completion_reason : std::uint8_t {

        /** @name System-reserved reasons (0x00-0x0F) */
        ///@{
        finished = 0x00, /**< is_finished() returned true: natural completion. Framework-only; never pass this to complete_task. */
        aborted  = 0x01, /**< Generic reason for a forced completion; complete_task callers must always supply a reason explicitly. */
        ///@}

        /** @name User-defined reasons (0x10-0x3F) */
        ///@{
        user_defined_start = 0x10, /**< base for caller-supplied reasons passed to complete_task. */
        ///@}

        max = 0x3F /**< Highest representable value: 6 bits, `0b00111111`. */
    };

    /**
    * @brief True if the reason belongs to the system-reserved range.
    * @param reason Completion reason to test.
    * @return `true` for 0x00-0x0F, otherwise `false`.
    */
    [[nodiscard]] constexpr bool is_system_reason(completion_reason reason) noexcept;

    /**
    * @brief True if the reason belongs to the caller-supplied range.
    * @param reason Completion reason to test.
    * @return `true` for 0x10-0x3F, otherwise `false`.
    */
    [[nodiscard]] constexpr bool is_user_reason(completion_reason reason) noexcept;

    /**
    * @brief True if the reason fits within the 6-bit canonical range.
    * @param reason Completion reason to test.
    * @return `true` for `reason <= completion_reason::max` (0x3F), otherwise `false`.
    */
    [[nodiscard]] constexpr bool is_valid_reason(completion_reason reason) noexcept;

} // namespace etask::core
#include "completion_reason.inl"
#endif // ETASK_CORE_COMPLETION_REASON_HPP_
