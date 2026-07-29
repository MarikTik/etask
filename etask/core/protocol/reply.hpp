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
* payload into named fields, `reply` holds named fields and produces a packet.
* There is exactly one reply shape, used both for a concluded task's real
* result and for an immediate manager-API rejection (with an empty result) -
* `task::on_complete` always returns a `buffer<>` regardless of completion
* path, and the wire packet doesn't distinguish "successful" from "error"
* structurally, only via the `status_code` it carries.
*
* ## Payload only - addressing is the header's business
*
* `reply` writes the packet's **payload** and nothing else. Whether the frame
* also carries a `receiver_id` is a property of `Packet`'s topology, and that
* field lives in `Packet::header` - owned by `ecomm::protocol::packet_header`,
* not by this type. So `reply` does not know or care about addressing: the
* caller (see `external_channel`) sets `header.receiver_id` on the packet
* `to_packet()` hands back, in the one place that already knows the topology.
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
#include <etools/memory/buffer_view.hpp>
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
    * `result`, if any, starts at `sizeof(TaskUid) + sizeof(status_code)`.
    *
    * Header fields (`receiver_id` under an addressed topology, sequence number,
    * FCS) are not touched here - `to_packet()` returns a packet whose header
    * carries only its type/options, for the caller to address and the channel
    * to seal.
    *
    * @warning `result` is held as a non-owning `buffer_view`: whatever it views
    *          must outlive this object and any `to_packet()` call. Construct and
    *          consume a reply synchronously, in the same scope as the `buffer<>`
    *          its `result` view came from.
    */
    template<typename Packet, typename TaskUid>
    class reply {
    public:
        static_assert(
            Packet::payload_size >= sizeof(TaskUid) + sizeof(status_code),
            "Packet's payload is too small to carry a TaskUid and a status_code."
        );

        /**
        * @brief Captures the outcome this reply represents.
        *
        * @param uid    Identifier of the task that produced the result.
        * @param code   Status describing the outcome.
        * @param result The task's result bytes; empty for a rejection.
        */
        reply(TaskUid uid, status_code code, etools::memory::buffer_view result) noexcept;

        /**
        * @brief Materializes the packet: header type/options set, payload packed.
        *
        * @note Addressing is the caller's to apply - assign
        *       `header.receiver_id` on the returned packet when `Packet`'s
        *       topology has node ids.
        */
        [[nodiscard]] Packet to_packet() const noexcept;

    private:
        TaskUid _uid;
        status_code _code;
        etools::memory::buffer_view _result;
    };

} // namespace etask::core::protocol

#include "reply.tpp"
#endif // ETASK_CORE_PROTOCOL_REPLY_HPP_
