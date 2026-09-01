/**
* @file request_builder.hpp
*
* @brief Builds the request frames the harness feeds to the channel.
*
* @note User-owned (support/). Not generated.
*
* ## Why this exists here rather than in the framework
*
* `etask::core::protocol::request` is a *reader*: it parses an inbound payload
* into a directive, a uid and an argument view. There is no writer beside it,
* because on a device nothing ever needs one - requests arrive, they are not
* composed. The peer that composes them is the Python client
* (`etask.protocol.build_request`), and it lives on the other end of the wire.
*
* This project's harness stands in for that peer inside the firmware process, so
* it needs the writing half. What follows is the same layout
* `protocol::request` reads and `build_request` writes:
*
* ```
* payload: [directive 1B][uid sizeof(TaskUid)][args...]
* ```
*
* Keeping it a few lines in `support/` rather than proposing it upstream is
* deliberate: a writer in the framework would be API surface every real firmware
* carries and none of it calls.
*/
#ifndef SUPPORT_REQUEST_BUILDER_HPP_
#define SUPPORT_REQUEST_BUILDER_HPP_
#include <cstddef>
#include <cstring>
#include <eser/flat/serializer.hpp>
#include <etask/core/completion_reason.hpp>
#include <etask/core/protocol/directive.hpp>

namespace support {

    /**
    * @class request_builder
    *
    * @brief Composes request packets for one link's packet type.
    *
    * @tparam RequestPacket The link's inbound packet type, from
    *         `generated/links.hpp`. The frame is sized by the schema, so
    *         arguments written here are guaranteed to fit any task's parameter
    *         list - `external_channel` static_asserts exactly that.
    * @tparam TaskUid The project's task identifier type (`global::task_id`).
    */
    template<typename RequestPacket, typename TaskUid>
    class request_builder {
    public:
        /// @brief Payload offset at which a task's argument bytes begin.
        static constexpr std::size_t args_offset = sizeof(std::byte) + sizeof(TaskUid);

        /**
        * @brief A request that starts a task, carrying its packed arguments.
        *
        * @tparam Args The argument types, in the task's declared wire order. The
        *         order is the wire contract: the codec is flat and tagless, so a
        *         swapped pair here is a silently different call, not an error.
        * @param uid The task to start.
        * @param args The constructor arguments, serialized exactly as the
        *        unpacking adapter on the other side will read them.
        * @return The frame, ready to hand to a hub.
        */
        template<typename... Args>
        static RequestPacket start(TaskUid uid, const Args&... args)
        {
            RequestPacket packet = frame(
                etask::core::protocol::directive::register_task,
                etask::core::completion_reason::finished,
                uid);
            if constexpr (sizeof...(Args) > 0) {
                // The same `eser::flat` serializer the framework unpacks with, so
                // the request half of the round trip is not a second, hand-rolled
                // encoder that could agree with this test while disagreeing with
                // the code under it.
                eser::flat::serialize(args...).to(
                    packet.payload + args_offset,
                    RequestPacket::payload_size - args_offset);
            }
            return packet;
        }

        /**
        * @brief A request that force-completes a running task.
        *
        * The reason travels in the directive byte's low six bits rather than in
        * the payload, which is why this is not `start` with a different
        * operation.
        *
        * @param uid The task to complete.
        * @param reason Why, as the task's `on_complete` will see it.
        * @return The frame, ready to hand to a hub.
        */
        static RequestPacket complete(TaskUid uid, etask::core::completion_reason reason)
        {
            return frame(etask::core::protocol::directive::complete_task, reason, uid);
        }

    private:
        /**
        * @brief The directive byte and uid every request opens with.
        *
        * @param command Which manager operation the frame invokes.
        * @param reason The completion reason packed alongside it; ignored by the
        *        manager for every command but `complete_task`.
        * @param uid The task the frame addresses.
        * @return A packet with its two header fields written and the argument
        *         region left zeroed.
        */
        static RequestPacket frame(
            etask::core::protocol::directive::operation command,
            etask::core::completion_reason reason,
            TaskUid uid)
        {
            RequestPacket packet{};
            packet.payload[0] =
                etask::core::protocol::directive{command, reason}.raw();
            // memcpy rather than a serialize call: the uid is raw bytes on the
            // wire - a straight copy of the enum, not a serialized value - which
            // is what lets the Python client read it with a plain
            // `int.from_bytes`. See etask.protocol's module docstring.
            std::memcpy(packet.payload + sizeof(std::byte), &uid, sizeof(TaskUid));
            return packet;
        }
    };

} // namespace support

#endif // SUPPORT_REQUEST_BUILDER_HPP_
