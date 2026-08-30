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
* - `Link`    - one link's `traits` from `generated/links.hpp`, carrying the two
*   `ecomm::protocol::packet<...>` instantiations this channel speaks, the
*   payload each direction must hold, the schema fingerprint, and which uids the
*   link accepts. Works under both `ecomm::protocol::topology::network` and
*   `topology::point_to_point` - see `protocol::request`/`protocol::reply` for
*   how addressing is handled (or isn't) in each case.
* - `Hub`     - anything exposing `try_receive<request_packet_t>() -> std::optional<...>`
*   and `send(reply_packet_t&) -> ecomm::protocol::send_result` - an `ecomm::hub<...>`
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
    * @brief A uid as the plain integer the wire carries.
    *
    * A generated project's `task_uid_t` is a scoped enum, so a link's
    * `carries()` - which knows the uid's *width* and nothing about the enum that
    * gives it meaning - cannot be handed one directly. A hand-written manager may
    * use a plain integer instead, and `std::underlying_type` may only be asked
    * about an enum, so the two cases are separated here rather than at the call
    * site.
    *
    * Deliberately not in a `detail` namespace of this one: `etask::core::detail`
    * already exists and is used unqualified from this file, and a nested
    * `channels::detail` would shadow it.
    *
    * @tparam Uid The manager's uid type: a scoped enum, or an integer.
    * @param uid The uid to strip.
    * @return The same value, as the integer type the wire carries.
    */
    template<typename Uid>
    [[nodiscard]] constexpr auto raw_uid(Uid uid) noexcept
    {
        if constexpr (std::is_enum_v<Uid>) {
            return static_cast<std::underlying_type_t<Uid>>(uid);
        } else {
            return uid;
        }
    }

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
    * ## One link, one type
    *
    * The two packets, the payload each direction must carry, the schema
    * fingerprint and the set of uids this link accepts are not independent
    * choices - they all follow from one link's entry in the schema. So they
    * arrive as one type rather than as five parameters: a call site that passed
    * them separately could pair one link's packets with another link's uid set,
    * and both would compile. `generated/links.hpp` emits a `traits` per link
    * that satisfies this; nothing else should need to.
    *
    * ## What this link carries
    *
    * A link may declare `subsystems:` in the schema, in which case it carries
    * only the tasks beneath them. That is what lets its frames be sized for the
    * widest task *it* carries rather than the widest on the device - often a
    * large saving, since subsystems differ in width. The same fact is enforced
    * at dispatch: a request naming a uid this link does not carry is refused
    * with `task_undefined_on_this_link` rather than run.
    *
    * @tparam Link A link's `traits` from `generated/links.hpp`. Supplies
    *         `request_packet_t`, `reply_packet_t`, `request_payload_need`,
    *         `reply_payload_need`, `fingerprint`, and `carries(uid)`.
    * @tparam Hub     Anything exposing `try_receive<request_packet_t>()` and
    *         `send(reply_packet_t&)`. Injected by reference at construction; not owned.
    * @tparam Manager A `task_manager<...>` instantiation. Injected by reference
    *         at construction; not owned.
    *
    * #### Responsibilities:
    *
    * - Poll `Hub` for inbound packets, parse via `protocol::request`.
    * - Refuse uids this link does not carry.
    * - Forward decoded requests to the injected task manager.
    * - Encode task results/errors via `protocol::reply` and send via `Hub`.
    */
    template<
        typename Link,
        typename Hub,
        typename Manager>
    class external_channel : public channel<typename Manager::task_uid_t> {
    public:
        /** @typedef task_uid_t
        * @brief The task identifier type, taken from `Manager::task_uid_t`.
        */
        using task_uid_t = typename Manager::task_uid_t;

        /** @typedef RequestPacket
        * @brief Inbound frames, sized for the widest request this link carries.
        */
        using RequestPacket = typename Link::request_packet_t;

        /** @typedef ReplyPacket
        * @brief Outbound frames, sized for the widest reply this link carries.
        */
        using ReplyPacket = typename Link::reply_packet_t;

        /// @brief The wire contract this link's peers must agree on.
        static constexpr std::uint64_t Fingerprint = Link::fingerprint;

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
        * @brief The packet must carry the largest request *this link* accepts.
        *
        * Both numbers are compile-time known - the packet's capacity from its
        * type, the demand from the link's own entry in the schema - but nothing
        * compared them until here, and getting it wrong is silent rather than
        * loud. The deserializer's own length check cannot catch it: it is handed
        * the packet's *capacity*, which by construction always satisfies it, so a
        * task whose arguments do not fit is built from zero-fill and run. On a
        * vehicle that is a command executed with fabricated parameters.
        *
        * The demand is the link's, not the project's, because a link that
        * declares `subsystems:` carries only some of the device's tasks and is
        * sized for those. Checking against the widest task on the whole device
        * would reject every correctly-sized restricted link. What keeps that
        * safe is `carries()`: a task the link is not sized for is also a task it
        * refuses, so the two facts cannot come apart.
        */
        static_assert(
            RequestPacket::payload_size >= Link::request_payload_need,
            "This packet's payload cannot carry the largest task request this link "
            "accepts. Both figures come from generated/links.hpp and should agree "
            "by construction, so this firing means a hand-written packet type was "
            "paired with a generated link's traits - the compiler note below shows "
            "both numbers."
        );

        /**
        * @brief The link's own requirement must cover the fixed request fields.
        *
        * A guard on the generator rather than on the user: `request_payload_need`
        * is emitted as a literal, and a literal that did not leave room for the
        * directive byte and the uid would misparse every frame rather than fail
        * to build. `sizeof(task_uid_t)` is the manager's view of the uid width
        * and the generated literal is the schema's, so this also catches the two
        * disagreeing - which would mean the C++ and the schema were generated
        * from different uid widths.
        */
        static_assert(
            Link::request_payload_need >= request_header_size,
            "This link's request_payload_need is too small for the directive byte "
            "and the uid that every request begins with. Regenerate; if it "
            "persists, the generated uid width and the manager's task_uid_t "
            "disagree."
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
