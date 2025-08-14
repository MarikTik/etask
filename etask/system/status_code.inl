// SPDX-License-Identifier: BSL-1.1
/**
* @file status_code.inl
*
* @brief Definition of status_code.hpp api.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-08-11
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_SYSTEM_STATUS_CODE_INL_
#define ETASK_SYSTEM_STATUS_CODE_INL_
#include "status_code.hpp"
namespace etask::system{
    constexpr bool is_manager_status(status_code code) noexcept {
        return static_cast<std::uint8_t>(code) < 0x20;
    }

    constexpr bool is_task_status(status_code code) noexcept {
        const auto v = static_cast<std::uint8_t>(code);
        return v >= 0x20 && v < static_cast<std::uint8_t>(custom_error_start);
    }

    constexpr bool is_custom_status(status_code code) noexcept{
        return static_cast<std::uint8_t>(code) >= 0x70;
    }
}

#endif //ETASK_SYSTEM_STATUS_CODE_INL_