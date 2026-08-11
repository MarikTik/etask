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

    template<typename Packet, typename Hub, typename Manager>
    external_channel<Packet, Hub, Manager>::external_channel(Hub& hub, Manager& manager) noexcept
        : _hub{hub}, _manager{manager}
    {
    }

    template<typename Packet, typename Hub, typename Manager>
    void external_channel<Packet, Hub, Manager>::address_and_send(
        Packet& out,
        [[maybe_unused]] std::uint8_t initiator_id)
    {
        // Addressing is a header field, applied here - the one place that knows
        // this Packet's topology.
        if constexpr (Packet::header_t::has_node_ids)
            out.header.receiver_id = initiator_id;

        (void)_hub.send(out);
    }

    template<typename Packet, typename Hub, typename Manager>
    void external_channel<Packet, Hub, Manager>::complete(
        std::uint8_t initiator_id,
        task_uid_t uid,
        status_code code,
        completion_reason reason,
        task<task_uid_t>& t)
    {
        // Build the reply packet with its uid+code header laid out; the result
        // region (payload + result_offset) starts zeroed.
        using reply_t = protocol::reply<Packet, task_uid_t>;
        Packet out = reply_t::make(uid, code);

        {
            // Point outcome's writer at this packet's result region, then let the
            // task pack `return {...}` straight into it - no heap, no copy.
            detail::result_region_scope region{
                out.payload + reply_t::result_offset,
                Packet::payload_size - reply_t::result_offset
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

    template<typename Packet, typename Hub, typename Manager>
    void external_channel<Packet, Hub, Manager>::update()
    {
        auto received = _hub.template try_receive<Packet>();
        if (received)
            dispatch(*received);
    }

    template<typename Packet, typename Hub, typename Manager>
    void external_channel<Packet, Hub, Manager>::dispatch(const Packet& packet)
    {
        protocol::request<Packet, task_uid_t> req{packet};

        // `request` parses the payload only; the originator is a header field,
        // read here - the one place that knows this Packet's topology.
        std::uint8_t initiator_id;
        if constexpr (Packet::header_t::has_node_ids) {
            initiator_id = packet.header.sender_id;
        } else {
            initiator_id = protocol::no_addressing_id;
        }

        status_code code;
        switch (req.command()) {
            case protocol::directive::register_task:
                // Placeholder: forward the args buffer_view as-is, matching
                // task_manager's current contract
                // (is_constructible_v<Task, buffer_view>). Unpacking into typed,
                // per-task constructor arguments is future work - see external_channel.hpp.
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
            Packet out = protocol::reply<Packet, task_uid_t>::make(req.uid(), code);
            address_and_send(out, initiator_id);
        }
    }

} // namespace etask::core::channels

#endif // ETASK_CORE_CHANNELS_EXTERNAL_CHANNEL_TPP_
