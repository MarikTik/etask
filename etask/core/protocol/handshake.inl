// SPDX-License-Identifier: MIT
/**
* @file handshake.inl
*
* @brief Definition of handshake.hpp api.
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
#ifndef ETASK_CORE_PROTOCOL_HANDSHAKE_INL_
#define ETASK_CORE_PROTOCOL_HANDSHAKE_INL_
#include "handshake.hpp"

namespace etask::core::protocol {

    constexpr handshake::handshake(std::uint64_t local_fingerprint) noexcept
        : _local_fingerprint(local_fingerprint)
    {}

    inline void handshake::local_preamble(std::byte* out) const noexcept
    {
        preamble::encode(out, _local_fingerprint);
    }

    inline status_code handshake::on_peer_preamble(const std::byte* in) noexcept
    {
        if (_state == handshake_state::mismatched) {
            // Already refused. Re-deciding here would let a peer overturn a
            // verdict by simply sending again; see the declaration's docstring.
            return status_code::schema_mismatch;
        }

        std::uint64_t peer = 0;
        const preamble_error error = preamble::decode(in, _local_fingerprint, &peer);

        _last_error = error;
        // Left at 0 when `decode` did not reach the fingerprint field: the bytes
        // were not a preamble, so there is no peer schema id to report.
        _peer_fingerprint = (error == preamble_error::none ||
                             error == preamble_error::fingerprint_mismatch)
            ? peer
            : 0;
        _state = (error == preamble_error::none) ? handshake_state::ready
                                                 : handshake_state::mismatched;

        return preamble::to_status(error);
    }

    inline status_code handshake::fail(preamble_error error) noexcept
    {
        _state      = handshake_state::mismatched;
        _last_error = error;
        return status_code::schema_mismatch;
    }

    inline void handshake::reset() noexcept
    {
        _state            = handshake_state::pending;
        _last_error       = preamble_error::none;
        _peer_fingerprint = 0;
    }

    constexpr handshake_state handshake::state() const noexcept
    {
        return _state;
    }

    constexpr bool handshake::is_ready() const noexcept
    {
        return _state == handshake_state::ready;
    }

    constexpr std::uint64_t handshake::local_fingerprint() const noexcept
    {
        return _local_fingerprint;
    }

    constexpr std::uint64_t handshake::peer_fingerprint() const noexcept
    {
        return _peer_fingerprint;
    }

    constexpr preamble_error handshake::last_error() const noexcept
    {
        return _last_error;
    }

} // namespace etask::core::protocol
#endif // ETASK_CORE_PROTOCOL_HANDSHAKE_INL_
