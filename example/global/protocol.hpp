// SPDX-License-Identifier: BSL-1.1
/**
* @file global_protocol.hpp
*
* @brief Application-level packet wiring: choose packet layout and checksum policy.
*
* This header is intended to be edited by the user. It centralizes the choice of
* packet format for the application and exposes a single alias `packet_t` used
* elsewhere in the codebase.
*
* Two ready-made packet layouts are provided:
*  - `basic_packet<Size, Id>`: minimal framing with no checksum field.
*  - `framed_packet<Size, Id, ChecksumPolicy>`: framing that includes a checksum
*    field whose type/size is defined by a policy.
*
* @note Use `basic_packet` on “smart” links that already guarantee integrity, e.g. TCP.
*
* @note Use `framed_packet` on simple/byte-stream links (e.g. UART, SPI, raw radio),
*       where link-layer integrity is not guaranteed.
*
* @note The first template parameter (`Size`) is the **full packet size in bytes**
*       (header + payload + checksum if present). Tune this to your application.
*
* @warning If you select `framed_packet`, pick a checksum policy that matches your
*          link characteristics and budget. Stronger policies cost more bytes and cycles.
*
* @see etask::comm::protocol::sum8, sum16, sum32
* @see etask::comm::protocol::crc8, crc16, crc32, crc64
* @see etask::comm::protocol::fletcher16, fletcher32
* @see etask::comm::protocol::adler32
* @see etask::comm::protocol::internet16
*
* @example
* // For UART at 115200 bps, 32-byte packets, and strong integrity:
* using uart_packet_t = etask::comm::protocol::framed_packet<32, global::task_id, etask::comm::protocol::crc16>;
*
* // For TCP sockets (already has checksums), keep it lightweight:
* using tcp_packet_t  = etask::comm::protocol::basic_packet<64, global::task_id>;
*
* @author
* Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-08-10
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef GLOBAL_PROTOCOL_HPP_
#define GLOBAL_PROTOCOL_HPP_
#include <etask/comm/protocol/protocol.hpp>
#include "task_id.hpp"
namespace global{

    /**
    * @typedef fpacket_t
    * 
    * @brief Framed packet with checksum field.
    *
    * @tparam 32 Full packet size in bytes (header + payload + checksum).
    * 
    * @tparam task_id Application’s task identifier enum used as the message discriminator.
    * 
    * @tparam etask::comm::protocol::crc32
    *         Checksum policy. Replace with any available policy from checksum.hpp.
    *
    * @note Replace `crc32` with another policy if you need a different trade-off
    *       (e.g., `crc16` for shorter packets, `sum8` for very low-cost links).
    * 
    * @see etask::comm::protocol (checksum policies listed in checksum.hpp)
    */
    using fpacket_t = etask::comm::protocol::framed_packet<
        32,
        task_id,
        etask::comm::protocol::crc32
    >;


    /**
    * @typedef bpacket_t
    * @brief Basic packet with no checksum.
    *
    * @tparam 32      Full packet size in bytes (header + payload).
    * 
    * @tparam task_id Discriminator for routing/decoding.
    *
    * @note No checksum or FCS is included. Prefer this when the transport already
    *       provides integrity (e.g., TCP) or when overhead must be minimal and
    *       corruption risk is acceptable.
    */
    using bpacket_t = etask::comm::protocol::basic_packet<
        32,
        task_id
    >;

    /**
    * @typedef packet_t
    * @brief Application-selected packet type used throughout the codebase.
    *
    * @note Change this alias to switch between `bpacket_t` and `fpacket_t`
    *       (or a differently parameterized variant) without touching the rest
    *       of the application.
    * @todo Review your transport. For UART/serial, set `packet_t = fpacket_t`.
    *       For TCP or other checked transports, `packet_t = bpacket_t` is sufficient.
    */
    using packet_t = bpacket_t; 

} // namespace global
#endif // GLOBAL_PROTOCOL_HPP_