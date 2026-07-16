// SPDX-License-Identifier: MIT
/**
* @file directive.inl
*
* @brief Definition of directive.hpp api.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-07-13
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_PROTOCOL_DIRECTIVE_INL_
#define ETASK_CORE_PROTOCOL_DIRECTIVE_INL_
#include "directive.hpp"

namespace etask::core::protocol {

    constexpr directive::directive(operation cmd, completion_reason reason) noexcept
        : _raw{static_cast<std::byte>(
            (static_cast<std::uint8_t>(cmd) << reason_bits) |
            (static_cast<std::uint8_t>(reason) & ((1u << reason_bits) - 1))
        )}
    {
    }

    constexpr directive::directive(std::byte raw) noexcept
        : _raw{raw}
    {
    }

    constexpr directive::operation directive::command() const noexcept
    {
        return static_cast<operation>(static_cast<std::uint8_t>(_raw) >> reason_bits);
    }

    constexpr completion_reason directive::reason() const noexcept
    {
        return static_cast<completion_reason>(
            static_cast<std::uint8_t>(_raw) & ((1u << reason_bits) - 1)
        );
    }

    constexpr std::byte directive::raw() const noexcept
    {
        return _raw;
    }

} // namespace etask::core::protocol
#endif // ETASK_CORE_PROTOCOL_DIRECTIVE_INL_
