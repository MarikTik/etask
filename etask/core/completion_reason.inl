// SPDX-License-Identifier: MIT
/**
* @file completion_reason.inl
*
* @brief Definition of completion_reason.hpp api.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-07-13
*
* @copyright
* MIT License
* Copyright (c) 2025 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_COMPLETION_REASON_INL_
#define ETASK_CORE_COMPLETION_REASON_INL_
#include "completion_reason.hpp"
namespace etask::core {
    constexpr bool is_system_reason(completion_reason reason) noexcept {
        return static_cast<std::uint8_t>(reason) < static_cast<std::uint8_t>(completion_reason::user_defined_start);
    }

    constexpr bool is_user_reason(completion_reason reason) noexcept {
        return not is_system_reason(reason);
    }

    constexpr bool is_valid_reason(completion_reason reason) noexcept {
        return reason <= completion_reason::max;
    }

    constexpr completion_reason user_reason(std::uint8_t n) noexcept {
        return static_cast<completion_reason>(
            static_cast<std::uint8_t>(completion_reason::user_defined_start) + n);
    }
}
#endif //ETASK_CORE_COMPLETION_REASON_INL_
