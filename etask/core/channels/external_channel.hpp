// SPDX-License-Identifier: MIT
/**
* @file external_channel.hpp
*
* @brief Declares the external communication channel bridging wire packets to
*        a task manager.
*
* @ingroup etask_core etask::core::channels
*
* `external_channel` is the counterpart to `internal_channel`: where
* `internal_channel` serves tasks initiated from within the same device,
* `external_channel` serves tasks requested by another device over the wire,
* via an `ecomm` hub/channel.
*
* ## Dependency injection
*
* Like `internal_channel`, this is core library mechanism, parameterized on
* the concrete types it needs rather than reaching for global names:
*
* - `RequestPacket` / `ReplyPacket` - the concrete `ecomm::protocol::packet<...>`
*   instantiations this
*   channel speaks. Works under both `ecomm::protocol::topology::network` and
*   `topology::point_to_point` - see `protocol::request`/`protocol::reply` for
*   how addressing is handled (or isn't) in each case.
* - `Hub`     - anything exposing `try_receive<RequestPacket>() -> std::optional<RequestPacket>`
*   and `send(ReplyPacket&) -> ecomm::protocol::send_result` - an `ecomm::hub<...>`
*   or a single `ecomm::channels::channel<Impl, Packet>` both satisfy this.
* - `Manager` - a `task_manager<...>` instantiation, exactly as for
*   `internal_channel`.
*
* ## Wire payload schema
*
* `ecomm::protocol::packet` imposes no application-layer schema on its
* `payload` (see its own docstring): task ids, commands, and status codes are
* not header fields in the current protocol version. `etask::core::protocol`
* (`request`/`reply`/`directive`) defines and owns that schema; this class
* only orchestrates polling, dispatch, and sending.
*
* @note Unpacking the trailing payload bytes into *typed, per-task* constructor
*       arguments (rather than a single `buffer_view`) is future work; today's
*       `task_manager` already expects exactly one `buffer_view` constructor
*       argument, so forwarding the raw remaining bytes is today's real
*       contract, not a placeholder shortcut. It will need revisiting once
*       tasks gain native-typed constructors.
*
* @see protocol/request.hpp, protocol/reply.hpp for the wire schema.
* @see internal_channel for the analogous system-initiated counterpart.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-07-13
*
* @copyright
* MIT License
* Copyright (c) 2025 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_CHANNELS_EXTERNAL_CHANNEL_HPP_
#define ETASK_CORE_CHANNELS_EXTERNAL_CHANNEL_HPP_
#include "../channel.hpp"
#include "../status_code.hpp"
#include "../completion_reason.hpp"
#include "../outcome.hpp"
#include "../protocol/protocol.hpp"
#include "../detail/result_region.hpp"
#include <cstdint>
#include <type_traits>

namespace etask::core::channels {

    namespace protocol = etask::core::protocol;

    /**
    * @class external_channel
    *
    * @brief Channel implementation for tasks requested by another device over the wire.
    *
    * ## Two packet types, one wire
    *
    * A request carries a task's *arguments*; a reply carries its *result*. Those
    * are different sizes - often very different, and either may be the larger -
    * so this channel is parameterized on one packet type per direction rather
    * than on a single type big enough for both. Both are generated from the
    * schema with the same topology, sequencing and checksum, so they share a
    * header type and are the same wire format; only the frame length differs.
    *
    * Sizing each direction for itself is the whole saving: the common case on a
    * control link is a small command producing a large telemetry reply, and a
    * single packet type would inflate every command to the size of the widest
    * result.
    *
    * A project that wants one size for both simply passes the same type twice.
    *
    * @tparam RequestPacket  Inbound frames: `ecomm::protocol::packet<...>`, sized
    *         for the widest task's arguments.
    * @tparam ReplyPacket    Outbound frames: sized for the widest task's result.
    *         Must share `RequestPacket`'s header type - same link, same format.
    * @tparam Hub     Anything exposing `try_receive<RequestPacket>()` and
    *         `send(ReplyPacket&)`. Injected by reference at construction; not owned.
    * @tparam Manager A `task_manager<...>` instantiation. Injected by reference
    *         at construction; not owned.
    *
    * #### Responsibilities:
    *
    * - Poll `Hub` for inbound packets, parse via `protocol::request`.
    * - Forward decoded requests to the injected task manager.
    * - Encode task results/errors via `protocol::reply` and send via `Hub`.
    */
    template<
        typename RequestPacket,
        typename ReplyPacket,
        typename Hub,
        typename Manager,
        std::uint64_t Fingerprint = protocol::no_fingerprint>
    class external_channel : public channel<typename Manager::task_uid_t> {
    public:
        /** @typedef task_uid_t
        * @brief The task identifier type, taken from `Manager::task_uid_t`.
        */
        using task_uid_t = typename Manager::task_uid_t;

    private:
        /**
        * @brief Both directions must be the same wire format.
        *
        * The two packet types differ only in length; a difference in topology,
        * sequencing or checksum would mean the peer is parsing a header this
        * channel never writes. Generated links cannot get this wrong, but a
        * hand-written pair can.
        */
        static_assert(
            std::is_same_v<typename RequestPacket::header_t, typename ReplyPacket::header_t>,
            "A link's request and reply packets must share a header type: same "
            "topology, sequencing and checksum. Only their length may differ."
        );

        /// @brief Payload bytes a request spends before a task's arguments begin.
        static constexpr std::size_t request_header_size =
            sizeof(std::byte) + sizeof(task_uid_t);

        /**
        * @brief The payload a request must carry: the directive, the uid, and the
        *        arguments of whichever task asks for the most.
        */
        static constexpr std::size_t request_payload_need =
            request_header_size + Manager::max_params_size;

        /**
        * @brief The packet must be able to carry this project's largest request.
        *
        * Both numbers are compile-time known - the packet's capacity from its
        * type, the schema's demand from the generated task list - but nothing
        * compared them until here, and getting it wrong is silent rather than
        * loud. The deserializer's own length check cannot catch it: it is handed
        * the packet's *capacity*, which by construction always satisfies it, so a
        * task whose arguments do not fit is built from zero-fill and run. On a
        * vehicle that is a command executed with fabricated parameters.
        *
        * If this fires, the packet in `config/` is too small for the schema:
        * raise its size to at least `request_payload_need` plus the header its
        * topology and checksum policy need.
        */
        static_assert(
            RequestPacket::payload_size >= request_payload_need,
            "This packet's payload cannot carry the project's largest task request. "
            "The schema needs `1 + sizeof(task_uid) + the widest task's params` "
            "bytes; the packet type in your config provides fewer - the compiler "
            "note below this one shows both figures. Enlarge PacketSize (keeping it "
            "a multiple of sizeof(std::size_t)), or shrink the widest task's params."
        );

    public:

        /**
        * @brief Binds this channel to the hub and manager it bridges between.
        * @param hub     Transport this channel polls/sends through. Must outlive
        *        this channel; held by reference, not owned.
        * @param manager The task manager this channel drives. Must outlive
        *        this channel; held by reference, not owned.
        */
        external_channel(Hub& hub, Manager& manager) noexcept;

        /// @brief Deleted copy constructor - an adapter bound to one hub/manager pair.
        external_channel(const external_channel&) = delete;
        /// @brief Deleted copy assignment - see the deleted copy constructor.
        external_channel& operator=(const external_channel&) = delete;
        /// @brief Deleted move constructor - see the deleted copy constructor.
        external_channel(external_channel&&) = delete;
        /// @brief Deleted move assignment - see the deleted copy constructor.
        external_channel& operator=(external_channel&&) = delete;

        /**
        * @brief Concludes a task and sends its result back to the requester.
        *
        * Builds the reply packet (uid + code), designates its payload result
        * region, calls `t.on_complete(reason)` so the task's `outcome` is packed
        * **directly into that packet** (no heap, no copy), settles the final
        * status code, addresses it to `initiator_id` when the link's topology
        * carries addressing, and sends it through the injected hub.
        *
        * @param initiator_id Device id of the original requester (or
        *        `protocol::no_addressing_id` under a point-to-point topology).
        * @param uid  Unique identifier of the concluding task.
        * @param code Status code describing the outcome. This is the *default*:
        *        a task that returns `outcome{...}.with_status(...)` overrides it,
        *        and so does an over-large result (`result_too_large`).
        * @param reason Why the task is concluding; forwarded to `on_complete`.
        * @param t    The concluding task, invoked through its base.
        */
        void complete(
            std::uint8_t initiator_id,
            task_uid_t uid,
            status_code code,
            completion_reason reason,
            task<task_uid_t>& t
        ) override;

        /**
        * @brief Poll the hub for one inbound packet and dispatch it.
        *
        * Convenience wrapper for the self-polling case: pulls one packet from
        * the hub via `try_receive<RequestPacket>()` and, if present, forwards it to
        * `dispatch`. Use this when this channel owns the receive path.
        *
        * @note Call this periodically from the application's main loop.
        */
        void update();

        /**
        * @brief Dispatch an already-received packet to the task manager.
        *
        * Parses `packet` via `protocol::request` and forwards to the matching
        * `task_manager` operation. On any non-`ok` status, sends an error reply
        * (uid + status code, no result bytes) back to the sender.
        *
        * This is the push entry point: when receiving is done elsewhere - e.g.
        * an `ecomm::router` polling several packet types across channels - a
        * handler hands the decoded packet here rather than having this channel
        * poll a hub itself. Replies still go out through the injected `Hub`.
        *
        * @param packet The inbound request packet to interpret and act on.
        */
        void dispatch(const RequestPacket& packet);

        /**
        * @brief Sends this build's handshake preamble, unframed.
        *
        * Call once when the link comes up, before any task traffic. Both peers
        * send immediately rather than waiting to be spoken to: symmetric, one
        * round trip, and neither side can hang waiting for the other to start.
        *
        * @return `ok` once the bytes are away.
        */
        [[nodiscard]] status_code begin_handshake();

        /**
        * @brief Feeds a peer's preamble to the handshake.
        *
        * The caller is whoever owns the receive path - this channel's own
        * @ref update, or an outer reader on a stream transport that has scanned
        * for the magic. Until this succeeds, @ref dispatch refuses every frame:
        * a peer with a different header layout must never have its bytes handed
        * to a parser built for this build's layout.
        *
        * @param bytes At least `protocol::preamble::size` bytes, starting at the magic.
        * @return `ok` when the contracts match; `schema_mismatch` otherwise.
        */
        [[nodiscard]] status_code accept_handshake(const std::byte* bytes);

        /**
        * @brief Whether this link has agreed a wire contract and may carry traffic.
        * @return `true` once the peer's fingerprint matched this build's.
        */
        [[nodiscard]] bool is_ready() const noexcept;

        /**
        * @brief Returns the link to `pending`, discarding any verdict.
        *
        * Call when the link drops. The thing that reconnects may not be the
        * thing that disconnected - it may be a peer reflashed from a different
        * schema - so a previous agreement cannot be carried over.
        */
        void reset_handshake() noexcept;

    private:
        /**
        * @brief Applies addressing to an outbound reply packet and sends it.
        *
        * `receiver_id` is a header field, so it is set here - the one place that
        * knows the link's topology. Under a point-to-point topology there is
        * nothing to address and `initiator_id` goes unused. Shared by `complete`
        * (a task's real result, already packed into the payload) and `dispatch`'s
        * rejection path (a header-only packet with an error code).
        *
        * @param out          The reply packet to seal and send (moved through the hub).
        * @param initiator_id Reply destination; ignored when the link has no node ids.
        */
        void address_and_send(ReplyPacket& out, std::uint8_t initiator_id);

        Hub& _hub;
        Manager& _manager;

        /**
        * @brief This link's handshake state.
        *
        * Per link, not per device: a board may hold one peer that agrees and
        * another that does not, and refusing the second must not silence the
        * first.
        */
        protocol::handshake _handshake{Fingerprint};
    };

} // namespace etask::core::channels

#include "external_channel.tpp"
#endif // ETASK_CORE_CHANNELS_EXTERNAL_CHANNEL_HPP_
