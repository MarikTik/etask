/**
* @file loopback_hub.hpp
*
* @brief An in-process hub: requests are pushed in by the test, replies are
*        collected for it to read back.
*
* @note User-owned (support/). Not generated, and not a framework type - it is
*       this project's harness transport.
*
* ## Why a hub and not a socket
*
* `external_channel` is parameterized on its `Hub` rather than on a concrete
* transport (see its docstring): anything exposing
* `try_receive<RequestPacket>()` and `send(ReplyPacket&)` will do. That is the
* seam this project tests through.
*
* Using it here rather than a real socket is deliberate, and it is not a
* shortcut. What `many_returns` is asking is whether a task's `return {...}`
* lands as the right bytes in the reply frame - a question entirely above the
* transport, and one a socket would answer no more truthfully while adding a
* second process, a connection, and a class of timing failure that has nothing
* to do with result packing. Every layer that *does* bear on the answer is the
* real one: the real `external_channel`, the real `protocol::reply`, the real
* `outcome` packing into the real packet type generated from the schema. What
* comes out of `sent()` is the frame that would have gone down the wire, byte
* for byte, so the host driver decodes exactly what a peer would have received.
*
* The transport this project *does* build for a board is PlatformIO's; see
* platformio.ini. This header is compiled on both targets so the two builds
* differ only in their entry point.
*/
#ifndef SUPPORT_LOOPBACK_HUB_HPP_
#define SUPPORT_LOOPBACK_HUB_HPP_
#include <cstddef>
#include <optional>
#include <vector>
#include <ecomm/channels/send_result.hpp>

namespace support {

    /**
    * @class loopback_hub
    *
    * @brief Satisfies `external_channel`'s Hub contract against two queues.
    *
    * Inbound requests are queued by @ref deliver and handed to the channel one
    * per `update()`; outbound replies are appended to a vector @ref sent
    * exposes. Neither direction drops or reorders, so a test that sees a missing
    * reply is looking at a real one.
    *
    * @tparam RequestPacket This link's inbound packet type, from
    *         `generated/links.hpp`.
    * @tparam ReplyPacket This link's outbound packet type. Distinct from
    *         `RequestPacket` because the two directions are sized separately -
    *         which is itself part of what this project tests.
    */
    template<typename RequestPacket, typename ReplyPacket>
    class loopback_hub {
    public:
        /**
        * @brief Queues a request for the channel to pick up on its next update.
        *
        * @param packet The frame a peer would have sent. Copied, so the caller
        *        may reuse its buffer.
        */
        void deliver(const RequestPacket& packet)
        {
            _inbound.push_back(packet);
        }

        /**
        * @brief Hands the channel the next queued request, if any.
        *
        * The template parameter is the channel's, not ours: `external_channel`
        * calls `try_receive<RequestPacket>()` explicitly, so the signature has to
        * accept a type argument even though this hub speaks exactly one.
        *
        * @tparam Packet The packet type the channel asks for; always
        *         `RequestPacket` here.
        * @return The oldest queued request, or `std::nullopt` when none is
        *         waiting.
        */
        template<typename Packet>
        std::optional<Packet> try_receive()
        {
            if (_next == _inbound.size())
                return std::nullopt;
            return _inbound[_next++];
        }

        /**
        * @brief Records a reply the channel is sending.
        *
        * @param packet The sealed reply frame. Copied whole - header included -
        *        because the point of the harness is to inspect the bytes that
        *        would have gone out, not a summary of them.
        * @return Always `ok`: an in-process queue cannot fail to accept, and
        *         reporting a failure the transport did not have would test the
        *         channel's error path rather than its result path.
        */
        ecomm::channels::send_result send(ReplyPacket& packet)
        {
            _outbound.push_back(packet);
            return ecomm::channels::send_result::ok;
        }

        /**
        * @brief Every reply sent so far, oldest first.
        *
        * @return A reference to the outbound log; valid until the next @ref send.
        */
        [[nodiscard]] const std::vector<ReplyPacket>& sent() const noexcept
        {
            return _outbound;
        }

        /**
        * @brief Discards the outbound log.
        *
        * Called between cases so each one asserts against replies it caused,
        * rather than against a running total it has to index into.
        */
        void clear_sent() noexcept
        {
            _outbound.clear();
        }

    private:
        /// @brief Requests waiting to be handed to the channel.
        std::vector<RequestPacket> _inbound;

        /**
        * @brief How many of @ref _inbound have been handed over.
        *
        * An index rather than a pop, so a delivered request stays alive for the
        * duration of the run - a task built from a `buffer_view` over the
        * payload must not outlive the frame it views.
        */
        std::size_t _next = 0;

        /// @brief Replies the channel has sent.
        std::vector<ReplyPacket> _outbound;
    };

} // namespace support

#endif // SUPPORT_LOOPBACK_HUB_HPP_
