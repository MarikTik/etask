// SPDX-License-Identifier: MIT
/**
* @file preamble.inl
*
* @brief Definition of preamble.hpp api.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-27
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_PROTOCOL_PREAMBLE_INL_
#define ETASK_CORE_PROTOCOL_PREAMBLE_INL_
#include "preamble.hpp"

namespace etask::core::protocol {

    inline void preamble::encode(std::byte* out, std::uint64_t fingerprint) noexcept
    {
        for (std::size_t i = 0; i < magic_size; ++i) {
            out[magic_offset + i] = static_cast<std::byte>(magic[i]);
        }
        out[version_offset]  = static_cast<std::byte>(version);
        out[reserved_offset] = static_cast<std::byte>(reserved);

        // Big-endian by explicit shift, not by memcpy-and-hope: the most
        // significant byte goes out first regardless of how this host stores a
        // uint64_t, so an ESP32, an x86 test runner and the Python peer all put
        // the same byte on the wire. A memcpy here would be correct on exactly
        // one endianness and silently wrong on the other - the failure mode
        // being a "schema mismatch" between two builds of the same schema,
        // which sends the reader looking in entirely the wrong place.
        for (std::size_t i = 0; i < fingerprint_size; ++i) {
            const unsigned shift = static_cast<unsigned>((fingerprint_size - 1 - i) * 8);
            out[fingerprint_offset + i] =
                static_cast<std::byte>((fingerprint >> shift) & 0xFFu);
        }
    }

    inline std::uint64_t preamble::read_fingerprint(const std::byte* in) noexcept
    {
        std::uint64_t value = 0;
        for (std::size_t i = 0; i < fingerprint_size; ++i) {
            value = (value << 8) | static_cast<std::uint64_t>(
                std::to_integer<std::uint8_t>(in[fingerprint_offset + i])
            );
        }
        return value;
    }

    inline preamble_error preamble::decode(
        const std::byte* in,
        std::uint64_t expected,
        std::uint64_t* peer_fingerprint
    ) noexcept
    {
        for (std::size_t i = 0; i < magic_size; ++i) {
            if (in[magic_offset + i] != static_cast<std::byte>(magic[i])) {
                // Nothing past here is trustworthy: without the magic these
                // bytes are not known to be a preamble, so the fingerprint
                // field is not a fingerprint and `peer_fingerprint` is left
                // alone rather than filled with a number that would read like
                // a real peer's schema id.
                return preamble_error::bad_magic;
            }
        }

        if (std::to_integer<std::uint8_t>(in[version_offset]) != version) {
            return preamble_error::bad_version;
        }

        // The reserved byte is deliberately not checked - see its docstring.

        const std::uint64_t peer = read_fingerprint(in);
        if (peer_fingerprint != nullptr) {
            *peer_fingerprint = peer;
        }

        return peer == expected
            ? preamble_error::none
            : preamble_error::fingerprint_mismatch;
    }

    constexpr status_code preamble::to_status(preamble_error error) noexcept
    {
        return error == preamble_error::none ? status_code::ok
                                             : status_code::schema_mismatch;
    }

} // namespace etask::core::protocol
#endif // ETASK_CORE_PROTOCOL_PREAMBLE_INL_
