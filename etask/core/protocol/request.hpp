// SPDX-License-Identifier: MIT
/**
* @file request.hpp
*
* @brief A structured, parsed view over an incoming wire packet's payload.
*
* @ingroup etask_core etask::core::protocol
*
* `ecomm::protocol::packet` gives you a raw `std::byte payload[]`; `request`
* is the etask-defined structured accessor over that payload, in the same
* spirit as `ecomm::protocol::packet_header` being a structured accessor over
* the raw protocol byte - parse once at the boundary, work with named fields
* everywhere else.
*
* ## Payload only - addressing is the header's business
*
* `request` reads the packet's **payload** and nothing else. Whether the frame
* also carries a `sender_id` is a property of `Packet`'s topology, and that
* field lives in `Packet::header` - owned by `ecomm::protocol::packet_header`,
* not by this type. A caller that needs the originator reads
* `packet.header.sender_id` directly (see `external_channel`), in the one place
* that already knows the topology and still holds the packet.
*
* That split is what keeps this a single, unconditional class. A payload parser
* that also reached into the header would have to be specialized on the
* topology - which is exactly the complexity this avoids, and which does not
* survive a node that routes several packet types with different topologies
* (see `ecomm::router`). See `reply.hpp` for the mirror-image design on the
* outbound side.
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
#ifndef ETASK_CORE_PROTOCOL_REQUEST_HPP_
#define ETASK_CORE_PROTOCOL_REQUEST_HPP_
#include "directive.hpp"
#include "../completion_reason.hpp"
#include <etools/memory/buffer_view.hpp>
#include <cstdint>
#include <cstddef>

namespace etask::core::protocol {

    /**
    * @class request
    *
    * @brief Parses an incoming packet's payload into named request fields.
    *
    * Wire picture:
    * ```
    * Packet::payload :
    *   +------------------+-----------------------+-------------------------------+
    *   | packed      (1B) | uid  (sizeof(TaskUid)) | tail (command-specific, $)    |
    *   +------------------+-----------------------+-------------------------------+
    * packed : directive - operation (high 2 bits) | completion_reason (low 6 bits), see directive.hpp
    * uid    : TaskUid, raw bytes (memcpy, not a serialized form)
    * ($) tail, by command:
    *     register_task                             : remaining bytes -> buffer_view,
    *         forwarded as-is to the task constructor. Unpacking this into typed,
    *         per-task constructor arguments is future work; today's task_manager
    *         already expects exactly one buffer_view argument, so this is not a
    *         placeholder shortcut so much as today's actual contract.
    *     pause_task / resume_task / complete_task   : empty (complete_task's reason
    *         already travels packed into the `packed` byte above).
    * ```
    * `packed` is always at payload offset 0; `uid` immediately follows it;
    * `tail`, if any, starts at `1 + sizeof(TaskUid)`.
    *
    * Header fields (`sender_id` under an addressed topology, sequence number,
    * FCS) are not read here - the caller reads them off `Packet::header`.
    *
    * @warning Holds a reference to the `Packet` it was constructed from; the
    *          packet must outlive every request parsed from it.
    */
    template<typename Packet, typename TaskUid>
    class request {
    public:
        static_assert(
            Packet::payload_size >= sizeof(std::byte) + sizeof(TaskUid),
            "Packet's payload is too small to carry a directive and a TaskUid."
        );

        explicit request(const Packet& packet) noexcept;

        /** @brief Which task_manager operation this request asks for. */
        [[nodiscard]] directive::operation command() const noexcept;

        /** @brief The target task's uid. */
        [[nodiscard]] TaskUid uid() const noexcept;

        /**
        * @brief Why to force-complete the task. Only meaningful when
        *        `command() == directive::complete_task`.
        */
        [[nodiscard]] completion_reason reason() const noexcept;

        /**
        * @brief The task constructor argument bytes. Only meaningful when
        *        `command() == directive::register_task`.
        */
        [[nodiscard]] etools::memory::buffer_view args() const noexcept;

    private:
        const Packet& _packet;
    };

} // namespace etask::core::protocol

#include "request.tpp"
#endif // ETASK_CORE_PROTOCOL_REQUEST_HPP_
