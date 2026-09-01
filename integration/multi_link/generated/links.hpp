/**
* @file links.hpp
*
* @brief The packet types for this system's external links.
*
* 2 external links: bench, net. Each becomes a namespace holding two packet types - one
* per direction - plus the constants its channel needs.
*
* The two directions are sized independently: `protocol::request` and `protocol::reply`
* are separately templated, and the traffic is rarely symmetric (a one-byte command can
* produce a forty-byte telemetry reply). They share a header type, so it stays one wire
* format at two sizes rather than becoming two protocols.
*
* What is NOT here: which port, socket or pins the transport uses. The schema cannot
* know that. Instantiate the transport in config/wiring.hpp and hand it these types.
*
* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema
*          on every generate; hand edits are overwritten. Regenerate via the
*          CMake `etask-generate` target, or `etask generate`.
*/
#ifndef GENERATED_LINKS_HPP_
#define GENERATED_LINKS_HPP_
#include <cstddef>
#include <ecomm/protocol/packet.hpp>
#include <ecomm/protocol/packet_header.hpp>
#include <ecomm/protocol/checksum.hpp>
#include <ecomm/protocol/sequence.hpp>
#include <ecomm/protocol/topology.hpp>
#include <cstdint>

namespace generated {

    /**
    * @brief This schema's wire contract, reduced to eight bytes.
    *
    * Two peers built from the same schema agree on every uid, every argument
    * list, every result shape and every link's frame layout. Two peers built
    * from different ones may agree on all of the layout and none of the
    * meaning: the frames parse, the checksum passes, and this device runs the
    * wrong task with plausible-looking arguments. That is what this catches.
    *
    * Exchanged in a fixed handshake preamble at connect - fixed because two
    * peers that disagree about a header cannot use a normal frame to say so.
    * A link whose peer sends a different value refuses task traffic rather
    * than misreading it; the other links keep working.
    *
    * Derived from a canonical rendering of the schema, so reordering the YAML
    * cannot change it and any real contract change must.
    */
    inline constexpr std::uint64_t schema_fingerprint = 0x5A40B70F411E4861ULL;

} // namespace generated

namespace generated::links {

    /**
    * @brief Whether this system declares any external link.
    *
    * It does, so each one's namespace follows. Emitted either way so a config header
    * can include this file unconditionally and branch on the constant instead of on the
    * shape of the schema.
    */
    inline constexpr bool any = true;

    /**
    * @brief The packet size that carries `PayloadNeed` payload bytes.
    *
    * A packet's payload is `PacketSize - sizeof(header_t)`, and the header's width
    * depends on the link's topology, sequencing and checksum - and on the target's
    * layout rules. The generator cannot compute that, so it emits the payload
    * requirement (which it does know, from the schema) and this adds the header and
    * rounds up.
    *
    * The rounding is to a literal 8, NOT to `sizeof(std::size_t)`. ecomm asserts
    * `PacketSize % sizeof(std::size_t) == 0`, and that word is 8 on a 64-bit host but 4
    * on an ESP32 - so rounding to the local word would give the PC client and the
    * device two different frame sizes from one schema, and both would compile clean
    * before disagreeing on the wire. 8 is a multiple of 4, so one number satisfies
    * every target. The cost is under eight bytes per frame.
    *
    * The `+ 1` is division-then-increment, so the result is the next multiple of 8
    * *strictly above* header + payload, never equal to it. That is deliberate: ecomm's
    * other assert is `PacketSize > sizeof(header_t)`, and a total that landed exactly
    * on a multiple of 8 would otherwise round to itself. It costs a full 8 bytes in
    * that one case and buys an invariant that holds for every schema.
    *
    * @tparam PayloadNeed Payload bytes the direction must carry.
    * @tparam Header The link's header type, whose size is added.
    * @return The total packet size, a multiple of 8.
    */
    template<std::size_t PayloadNeed, typename Header>
    inline constexpr std::size_t packet_size_for =
        ((PayloadNeed + sizeof(Header)) / 8 + 1) * 8;

    /**
    * @brief The `bench` link, over uart.
    *
    * Carries `telemetry`, `shared`, and nothing else. Frames are sized for the widest
    * of those 2 task(s) rather than for the whole device, and a request for any other
    * uid is refused with `task_undefined_on_this_link` - the task exists, this wire
    * does not carry it.
    *
    * Topology `point_to_point`: this link has exactly one peer, so an address field
    * would be the same constant in every frame. Those two header bytes are not spent.
    *
    * Checksum `crc16`: the header carries an FCS field of that policy's width, because
    * a raw link corrupts frames silently, and sixteen bits is the cheapest width that
    * catches the burst errors such links actually produce.
    *
    * Reliable: the framework sequences frames and resends the unacknowledged ones, so
    * the header carries a one-byte sequence number. Sequencing is not a separate choice
    * - `reliable_channel` cannot match an acknowledgement to a frame without it, and
    * static_asserts on it - so it follows from reliability rather than being asked for.
    */
    namespace bench {

        /// @brief Whether frames name a destination.
        inline constexpr ecomm::protocol::topology link_topology =
            ecomm::protocol::topology::point_to_point;

        /// @brief Whether frames carry a sequence number.
        using sequence_policy = ecomm::protocol::sequenced;

        /// @brief The integrity policy frames carry.
        using checksum_policy = ecomm::protocol::crc16;

        /**
        * @brief The header both directions carry.
        *
        * One header type for the whole link, because `external_channel` static_asserts
        * that a link's request and reply packets share one: the two packets differ in
        * size, but they are the same wire format, and a link whose two directions
        * disagreed about topology or checksum would not be one link.
        */
        using header_t = ecomm::protocol::packet_header<
            link_topology, sequence_policy, checksum_policy>;

        /**
        * @brief Payload bytes a request must be able to carry.
        *
        * 2 fixed + 2 variable: the packed directive byte, the 1-byte uid, and the
        * widest task's arguments.
        *
        * The widest is `shared.echo` at 2 bytes, which is where a surprising number
        * comes from - change that task and this changes.
        */
        inline constexpr std::size_t request_payload_need = 4;

        /**
        * @brief Payload bytes a reply must be able to carry.
        *
        * 2 fixed + 3 variable: the 1-byte uid, the status byte, and the widest result
        * any task can reply with.
        *
        * The widest is `shared.echo on task_finished` at 3 bytes, which is where a
        * surprising number comes from - change that task and this changes.
        */
        inline constexpr std::size_t reply_payload_need = 5;

        /**
        * @brief The packet a request travels in.
        *
        * 4 bytes against the reply's 5: this direction is the smaller one, and sizing
        * both to the wider would spend the difference in every buffer for nothing.
        *
        * Its size is the payload requirement plus this link's header, rounded up to a
        * multiple of 8 - computed by the compiler, since only it knows how wide the
        * header is on this target. See `packet_size_for`.
        */
        using request_packet_t = ecomm::protocol::packet<
            packet_size_for<request_payload_need, header_t>,
            link_topology, sequence_policy, checksum_policy>;

        /**
        * @brief The packet a reply travels in.
        *
        * 5 bytes against the request's 4: this direction is the larger one, and sizing
        * both to the wider would spend the difference in every buffer for nothing.
        *
        * Its size is the payload requirement plus this link's header, rounded up to a
        * multiple of 8 - computed by the compiler, since only it knows how wide the
        * header is on this target. See `packet_size_for`.
        */
        using reply_packet_t = ecomm::protocol::packet<
            packet_size_for<reply_payload_need, header_t>,
            link_topology, sequence_policy, checksum_policy>;

        /**
        * @brief Whether this link carries a task.
        *
        * This link declares `subsystems:`, so it carries only the uids beneath them. A
        * request for any other uid is refused before it is dispatched: the task exists
        * on this device, but not on this wire.
        *
        * @param uid The uid a request named.
        * @return Whether this link carries that task.
        */
        constexpr bool carries(std::uint8_t uid) noexcept
        {
            return
                uid == 0x4B or   // shared.echo
                uid == 0xE0;   // telemetry.sample
        }

        /**
        * @brief Whether to wrap this link's channel in `reliable_channel`.
        *
        * Read by config/wiring.hpp, which is where the channel is actually built: the
        * schema decides the policy, the user's file supplies the transport it applies
        * to.
        */
        inline constexpr bool reliable = true;

        /// @brief Resends before a frame is given up on.
        inline constexpr unsigned retries = 5;

        /// @brief How many unacknowledged frames may be in flight; sizes
        ///        the resend buffer, so it is this link's real memory cost.
        inline constexpr unsigned buffer_depth = 2;

        /**
        * @brief This link, as one type.
        *
        * What `external_channel` is instantiated on. Bundles the two packet types, the
        * payload each direction must carry, the schema fingerprint the handshake
        * exchanges, and which uids this link accepts - so a channel is built from one
        * name and cannot be handed a mismatched set.
        */
        struct traits {
            /// @brief The packet a request travels in.
            using request_packet_t = bench::request_packet_t;

            /// @brief The packet a reply travels in.
            using reply_packet_t = bench::reply_packet_t;

            /// @brief The wire contract both peers must agree on.
            static constexpr std::uint64_t fingerprint = generated::schema_fingerprint;

            /// @brief Payload bytes a request must carry. @see request_payload_need
            static constexpr std::size_t request_payload_need = bench::request_payload_need;

            /// @brief Payload bytes a reply must carry. @see reply_payload_need
            static constexpr std::size_t reply_payload_need = bench::reply_payload_need;

            /**
            * @brief Whether this link carries a uid.
            *
            * A static member function rather than a pointer to one, so the call is
            * resolved at compile time: on a link that carries everything the body is
            * `return true`, and the check disappears entirely.
            *
            * @param uid The uid a request named.
            * @return Whether this link carries that task.
            */
            static constexpr bool carries(std::uint8_t uid) noexcept
            { return bench::carries(uid); }
        };
    } // namespace bench

    /**
    * @brief The `net` link, over tcp.
    *
    * Carries `bulk`, `shared`, and nothing else. Frames are sized for the widest of
    * those 2 task(s) rather than for the whole device, and a request for any other uid
    * is refused with `task_undefined_on_this_link` - the task exists, this wire does
    * not carry it.
    *
    * Topology `network`: frames carry a sender and a receiver id, two header bytes,
    * because this link reaches more than one peer and a frame that did not name its
    * destination could not be routed.
    *
    * Checksum `none`: no FCS field in the header, because the transport already
    * checksums every byte it carries, so a second one would cost width without covering
    * anything the first misses.
    *
    * Not reliable: `tcp` already delivers every frame in order, so layering the
    * framework's own guarantee on top would add a sequence byte, a retry timer and a
    * resend buffer to re-guarantee what the transport has already guaranteed. No
    * sequence field.
    */
    namespace net {

        /// @brief Whether frames name a destination.
        inline constexpr ecomm::protocol::topology link_topology =
            ecomm::protocol::topology::network;

        /// @brief Whether frames carry a sequence number.
        using sequence_policy = ecomm::protocol::no_sequence;

        /// @brief The integrity policy frames carry.
        using checksum_policy = ecomm::protocol::none;

        /**
        * @brief The header both directions carry.
        *
        * One header type for the whole link, because `external_channel` static_asserts
        * that a link's request and reply packets share one: the two packets differ in
        * size, but they are the same wire format, and a link whose two directions
        * disagreed about topology or checksum would not be one link.
        */
        using header_t = ecomm::protocol::packet_header<
            link_topology, sequence_policy, checksum_policy>;

        /**
        * @brief Payload bytes a request must be able to carry.
        *
        * 2 fixed + 32 variable: the packed directive byte, the 1-byte uid, and the
        * widest task's arguments.
        *
        * The widest is `bulk.transfer` at 32 bytes, which is where a surprising number
        * comes from - change that task and this changes.
        */
        inline constexpr std::size_t request_payload_need = 34;

        /**
        * @brief Payload bytes a reply must be able to carry.
        *
        * 2 fixed + 20 variable: the 1-byte uid, the status byte, and the widest result
        * any task can reply with.
        *
        * The widest is `bulk.transfer on task_finished` at 20 bytes, which is where a
        * surprising number comes from - change that task and this changes.
        */
        inline constexpr std::size_t reply_payload_need = 22;

        /**
        * @brief The packet a request travels in.
        *
        * 34 bytes against the reply's 22: this direction is the larger one, and sizing
        * both to the wider would spend the difference in every buffer for nothing.
        *
        * Its size is the payload requirement plus this link's header, rounded up to a
        * multiple of 8 - computed by the compiler, since only it knows how wide the
        * header is on this target. See `packet_size_for`.
        */
        using request_packet_t = ecomm::protocol::packet<
            packet_size_for<request_payload_need, header_t>,
            link_topology, sequence_policy, checksum_policy>;

        /**
        * @brief The packet a reply travels in.
        *
        * 22 bytes against the request's 34: this direction is the smaller one, and
        * sizing both to the wider would spend the difference in every buffer for
        * nothing.
        *
        * Its size is the payload requirement plus this link's header, rounded up to a
        * multiple of 8 - computed by the compiler, since only it knows how wide the
        * header is on this target. See `packet_size_for`.
        */
        using reply_packet_t = ecomm::protocol::packet<
            packet_size_for<reply_payload_need, header_t>,
            link_topology, sequence_policy, checksum_policy>;

        /**
        * @brief Whether this link carries a task.
        *
        * This link declares `subsystems:`, so it carries only the uids beneath them. A
        * request for any other uid is refused before it is dispatched: the task exists
        * on this device, but not on this wire.
        *
        * @param uid The uid a request named.
        * @return Whether this link carries that task.
        */
        constexpr bool carries(std::uint8_t uid) noexcept
        {
            return
                uid == 0x1E or   // bulk.transfer
                uid == 0x4B;   // shared.echo
        }

        /**
        * @brief Whether to wrap this link's channel in `reliable_channel`.
        *
        * Read by config/wiring.hpp, which is where the channel is actually built: the
        * schema decides the policy, the user's file supplies the transport it applies
        * to.
        */
        inline constexpr bool reliable = false;

        // No `retries` or `buffer_depth` here: nothing is ever resent on an unreliable
        // link, so a retry budget would be a number no code reads.

        /**
        * @brief This link, as one type.
        *
        * What `external_channel` is instantiated on. Bundles the two packet types, the
        * payload each direction must carry, the schema fingerprint the handshake
        * exchanges, and which uids this link accepts - so a channel is built from one
        * name and cannot be handed a mismatched set.
        */
        struct traits {
            /// @brief The packet a request travels in.
            using request_packet_t = net::request_packet_t;

            /// @brief The packet a reply travels in.
            using reply_packet_t = net::reply_packet_t;

            /// @brief The wire contract both peers must agree on.
            static constexpr std::uint64_t fingerprint = generated::schema_fingerprint;

            /// @brief Payload bytes a request must carry. @see request_payload_need
            static constexpr std::size_t request_payload_need = net::request_payload_need;

            /// @brief Payload bytes a reply must carry. @see reply_payload_need
            static constexpr std::size_t reply_payload_need = net::reply_payload_need;

            /**
            * @brief Whether this link carries a uid.
            *
            * A static member function rather than a pointer to one, so the call is
            * resolved at compile time: on a link that carries everything the body is
            * `return true`, and the check disappears entirely.
            *
            * @param uid The uid a request named.
            * @return Whether this link carries that task.
            */
            static constexpr bool carries(std::uint8_t uid) noexcept
            { return net::carries(uid); }
        };
    } // namespace net

} // namespace generated::links
#endif // GENERATED_LINKS_HPP_
