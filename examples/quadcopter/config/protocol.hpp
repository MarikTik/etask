// SPDX-License-Identifier: MIT
/**
* @file protocol.hpp
*
* @brief The wire packet type this node speaks.
*
* @note User-owned config. Pick the packet shape that matches your physical
*       link, then use `config::packet_t` throughout the rest of the config.
*
* `ecomm::protocol::packet<PacketSize, Topology, SequencePolicy, ChecksumPolicy>`
* is a raw POD frame; etask layers its own application schema
* (directive + task id + args/result) into the packet's opaque payload - see
* `etask/core/protocol`. Tuning guide:
*
*  - PacketSize    total bytes on the wire. Must be a multiple of
*                  `sizeof(std::size_t)` and large enough to hold the etask
*                  payload (1 directive byte + sizeof(task_id) + your largest
*                  task's args/result). Bump this if a task's payload grows.
*  - Topology      `point_to_point` for a single-peer link (UART, one socket) -
*                  no sender/receiver id fields; `network` for a shared bus /
*                  mesh where replies must be addressed back to a sender.
*  - SequencePolicy `no_sequence`, or `sequenced` (required by reliable_channel).
*  - ChecksumPolicy `none` when the transport already guarantees integrity
*                  (TCP); `crc16`/`crc32`/`sum8`/... on raw links (UART, radio).
*/
#ifndef CONFIG_PROTOCOL_HPP_
#define CONFIG_PROTOCOL_HPP_
#include <ecomm/protocol/protocol.hpp>

namespace config {

    /**
    * @brief The application's wire packet. Referenced by the transport,
    *        external_channel, and router.
    *
    * Default: a 32-byte point-to-point frame with a CRC-16 checksum, a sensible
    * baseline for a UART/serial link. Change the template arguments to retune.
    */
    using packet_t = ecomm::protocol::packet<
        32,
        ecomm::protocol::topology::point_to_point,
        ecomm::protocol::no_sequence,
        ecomm::protocol::crc16
    >;

} // namespace config

#endif // CONFIG_PROTOCOL_HPP_
