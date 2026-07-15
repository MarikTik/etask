// SPDX-License-Identifier: BSL-1.1
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
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
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
}
#endif //ETASK_CORE_COMPLETION_REASON_INL_
