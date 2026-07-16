// SPDX-License-Identifier: MIT
/**
* @file wire_command.inl
*
* @brief Definition of wire_command.hpp api.
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
#ifndef ETASK_CORE_PROTOCOL_WIRE_COMMAND_INL_
#define ETASK_CORE_PROTOCOL_WIRE_COMMAND_INL_
#include "wire_command.hpp"

namespace etask::core::protocol {

    constexpr directive::directive(wire_command cmd, completion_reason reason) noexcept
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

    constexpr directive::wire_command directive::command() const noexcept
    {
        return static_cast<wire_command>(static_cast<std::uint8_t>(_raw) >> reason_bits);
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
#endif // ETASK_CORE_PROTOCOL_WIRE_COMMAND_INL_
