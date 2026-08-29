// SPDX-License-Identifier: MIT
/**
* @file external_channel.tpp
*
* @brief Definition of external_channel.hpp api.
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
#ifndef ETASK_CORE_CHANNELS_EXTERNAL_CHANNEL_TPP_
#define ETASK_CORE_CHANNELS_EXTERNAL_CHANNEL_TPP_
#include "external_channel.hpp"

namespace etask::core::channels {

    template<typename RequestPacket, typename ReplyPacket, typename Hub, typename Manager, std::uint64_t FP>
    external_channel<RequestPacket, ReplyPacket, Hub, Manager, FP>::external_channel(Hub& hub, Manager& manager) noexcept
        : _hub{hub}, _manager{manager}
    {
    }

    template<typename RequestPacket, typename ReplyPacket, typename Hub, typename Manager, std::uint64_t FP>
    void external_channel<RequestPacket, ReplyPacket, Hub, Manager, FP>::address_and_send(
        ReplyPacket& out,
        [[maybe_unused]] std::uint8_t initiator_id)
    {
        // Addressing is a header field, applied here - the one place that knows
        // this link's topology.
        if constexpr (ReplyPacket::header_t::has_node_ids)
            out.header.receiver_id = initiator_id;

        (void)_hub.send(out);
    }

    template<typename RequestPacket, typename ReplyPacket, typename Hub, typename Manager, std::uint64_t FP>
    void external_channel<RequestPacket, ReplyPacket, Hub, Manager, FP>::complete(
        std::uint8_t initiator_id,
        task_uid_t uid,
        status_code code,
        completion_reason reason,
        task<task_uid_t>& t)
    {
        // A task can only be live on this link if a request got through, which
        // requires a ready handshake - but a link can drop and reset while a task
        // is still running, and its result must not then go to a peer whose
        // contract this build no longer shares. `complete` overrides a void
        // channel method, so refusing means not sending; the task still concludes
        // and its slot is still freed by the manager.
        if (not is_ready())
            return;

        // Build the reply packet with its uid+code header laid out; the result
        // region (payload + result_offset) starts zeroed.
        using reply_t = protocol::reply<ReplyPacket, task_uid_t>;
        ReplyPacket out = reply_t::make(uid, code);

        {
            // Point outcome's writer at this packet's result region, then let the
            // task pack `return {...}` straight into it - no heap, no copy.
            detail::result_region_scope region{
                out.payload + reply_t::result_offset,
                ReplyPacket::payload_size - reply_t::result_offset
            };
            const outcome result = t.on_complete(reason);

            // The task may name the status the peer discriminates on (or the
            // outcome may force `result_too_large`), so the code byte is settled
            // only now - after on_complete, before the packet goes out. `ok` is
            // how an outcome says it named nothing; the manager's code stands.
            if (result.status() != status_code::ok)
                reply_t::set_code(out, result.status());
        }

        address_and_send(out, initiator_id);
    }

    template<typename RequestPacket, typename ReplyPacket, typename Hub, typename Manager, std::uint64_t FP>
    void external_channel<RequestPacket, ReplyPacket, Hub, Manager, FP>::update()
    {
        auto received = _hub.template try_receive<RequestPacket>();
        if (received)
            dispatch(*received);
    }

    template<typename RequestPacket, typename ReplyPacket, typename Hub, typename Manager, std::uint64_t FP>
    void external_channel<RequestPacket, ReplyPacket, Hub, Manager, FP>::dispatch(const RequestPacket& packet)
    {
        // Refused before parsing, not after: a peer that disagrees about header
        // layout would have its bytes read at the wrong offsets, and a frame that
        // happens to parse is exactly the dangerous case - plausible arguments for
        // the wrong task.
        if (not is_ready())
            return;

        protocol::request<RequestPacket, task_uid_t> req{packet};

        // `request` parses the payload only; the originator is a header field,
        // read here - the one place that knows this link's topology.
        std::uint8_t initiator_id;
        if constexpr (RequestPacket::header_t::has_node_ids) {
            initiator_id = packet.header.sender_id;
        } else {
            initiator_id = protocol::no_addressing_id;
        }

        status_code code;
        switch (req.command()) {
            case protocol::directive::register_task:
                // The args view is forwarded as-is; each manager wraps its own
                // tasks in the unpacking adapter, so a native-ctor task is built
                // from these bytes without this channel knowing its signature.
                code = _manager.register_task(this, initiator_id, req.uid(), req.args());
                break;
            case protocol::directive::pause_task:
                code = _manager.pause_task(req.uid());
                break;
            case protocol::directive::resume_task:
                code = _manager.resume_task(req.uid());
                break;
            case protocol::directive::complete_task:
                code = _manager.complete_task(req.uid(), req.reason());
                break;
            default:
                code = status_code::invalid_params;
                break;
        }

        if (code != status_code::ok) {
            // Rejection: a header-only reply (uid + error code, empty result).
            ReplyPacket out = protocol::reply<ReplyPacket, task_uid_t>::make(req.uid(), code);
            address_and_send(out, initiator_id);
        }
    }

    template<typename RequestPacket, typename ReplyPacket, typename Hub, typename Manager, std::uint64_t FP>
    status_code external_channel<RequestPacket, ReplyPacket, Hub, Manager, FP>::begin_handshake()
    {
        if constexpr (FP == protocol::no_fingerprint) {
            // No contract to assert, so nothing to send and nothing to wait for.
            return status_code::ok;
        }
        else {
            // A plain byte carrier: the preamble is deliberately not a packet,
            // because a peer that disagrees about header layout could not parse
            // one. Trivially copyable and exactly `size` bytes, so the same
            // transport write a packet uses carries it unchanged.
            struct frame { std::byte bytes[protocol::preamble::size]; };
            static_assert(sizeof(frame) == protocol::preamble::size,
                "the preamble frame must not acquire padding: it is a wire layout");

            frame out{};
            _handshake.local_preamble(out.bytes);
            (void)_hub.send(out);
            return status_code::ok;
        }
    }

    template<typename RequestPacket, typename ReplyPacket, typename Hub, typename Manager, std::uint64_t FP>
    status_code external_channel<RequestPacket, ReplyPacket, Hub, Manager, FP>::accept_handshake(
        const std::byte* bytes)
    {
        if constexpr (FP == protocol::no_fingerprint)
            return status_code::ok;
        else
            return _handshake.on_peer_preamble(bytes);
    }

    template<typename RequestPacket, typename ReplyPacket, typename Hub, typename Manager, std::uint64_t FP>
    bool external_channel<RequestPacket, ReplyPacket, Hub, Manager, FP>::is_ready() const noexcept
    {
        // A link with no fingerprint configured was never gated in the first
        // place; one with a fingerprint must have agreed it.
        return FP == protocol::no_fingerprint or _handshake.is_ready();
    }

    template<typename RequestPacket, typename ReplyPacket, typename Hub, typename Manager, std::uint64_t FP>
    void external_channel<RequestPacket, ReplyPacket, Hub, Manager, FP>::reset_handshake() noexcept
    {
        _handshake.reset();
    }

} // namespace etask::core::channels

#endif // ETASK_CORE_CHANNELS_EXTERNAL_CHANNEL_TPP_
