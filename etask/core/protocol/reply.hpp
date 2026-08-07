// SPDX-License-Identifier: MIT
/**
* @file reply.hpp
*
* @brief Builds an outgoing wire packet's payload from a task's
*        uid/status_code/result.
*
* @ingroup etask_core etask::core::protocol
*
* The counterpart to `request`: where `request` parses an incoming packet's
* payload into named fields, `reply` lays out the fixed header of an outgoing
* payload - the task uid and status code - and exposes where the result bytes go
* after it. There is exactly one reply shape, used both for a concluded task's
* real result and for an immediate manager-API rejection (empty result): the wire
* packet doesn't distinguish "successful" from "error" structurally, only via the
* `status_code` it carries.
*
* `reply` no longer copies a result in. A concluding task's `outcome` is packed
* **directly** into the returned packet's payload at @ref result_offset (see
* `external_channel::complete`); the rejection path just leaves that region zero.
* So `reply` is a small stateless helper: @ref make builds a header-laid-out
* packet, and @ref result_offset says where the result region begins.
*
* ## Payload only - addressing is the header's business
*
* `reply` writes the packet's **payload** and nothing else. Whether the frame
* also carries a `receiver_id` is a property of `Packet`'s topology, and that
* field lives in `Packet::header` - owned by `ecomm::protocol::packet_header`,
* not by this type. So `reply` does not know or care about addressing: the
* caller (see `external_channel`) sets `header.receiver_id` on the packet
* `make()` hands back, in the one place that already knows the topology.
*
* That split is what keeps this a single, unconditional class. A payload
* builder that also reached into the header would have to be specialized on
* the topology - which is exactly the complexity this avoids, and which does
* not survive a node that routes several packet types with different
* topologies (see `ecomm::router`).
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
#ifndef ETASK_CORE_PROTOCOL_REPLY_HPP_
#define ETASK_CORE_PROTOCOL_REPLY_HPP_
#include "../status_code.hpp"
#include <cstdint>
#include <cstddef>

namespace etask::core::protocol {

    /**
    * @class reply
    *
    * @brief Packs a task outcome into an outgoing packet's payload.
    *
    * Wire picture:
    * ```
    * Packet::payload :
    *   +-----------------------+----------------+-------------------------------+
    *   | uid (sizeof(TaskUid)) | code      (1B) | result (remaining bytes, $)   |
    *   +-----------------------+----------------+-------------------------------+
    * ($) truncated to fit `Packet::payload_size`; empty for an immediate
    *     manager-API rejection (no task ever ran to produce a result).
    * ```
    * `uid` is always at payload offset 0; `code` immediately follows it;
    * `result`, if any, starts at @ref result_offset.
    *
    * Header fields (`receiver_id` under an addressed topology, sequence number,
    * FCS) are not touched here - @ref make returns a packet whose header carries
    * only its type/options, for the caller to address and the channel to seal.
    */
    template<typename Packet, typename TaskUid>
    struct reply {
        static_assert(
            Packet::payload_size >= sizeof(TaskUid) + sizeof(status_code),
            "Packet's payload is too small to carry a TaskUid and a status_code."
        );

        /// @brief Payload offset at which a task's result bytes begin.
        static constexpr std::size_t result_offset = sizeof(TaskUid) + sizeof(status_code);

        /**
        * @brief Builds a reply packet with its header laid out and result region empty.
        *
        * Sets the packet's `header_type::data` (with the `error` option when
        * `code != ok`), writes `uid` at offset 0 and `code` right after, and leaves
        * the `result_offset`.. region zeroed for a task's `outcome` to pack into
        * (or to send as-is for a rejection).
        *
        * @param uid  Identifier of the task the reply is for.
        * @param code Status describing the outcome.
        * @return A packet ready to address (`header.receiver_id`) and seal/send.
        *
        * @note Addressing is the caller's to apply, in the one place that knows
        *       `Packet`'s topology (see `external_channel`).
        */
        [[nodiscard]] static Packet make(TaskUid uid, status_code code) noexcept;
    };

} // namespace etask::core::protocol

#include "reply.tpp"
#endif // ETASK_CORE_PROTOCOL_REPLY_HPP_
