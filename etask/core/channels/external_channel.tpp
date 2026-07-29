// SPDX-License-Identifier: BSL-1.1
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
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
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
    void external_channel<Packet, Hub, Manager>::send_reply(
        task_uid_t uid,
        status_code code,
        etools::memory::buffer_view result,
        [[maybe_unused]] std::uint8_t initiator_id)
    {
        protocol::reply<Packet, task_uid_t> rep{uid, code, result};
        auto out = rep.to_packet();

        // `reply` writes the payload only; addressing is a header field, applied
        // here - the one place that knows this Packet's topology.
        if constexpr (Packet::header_t::has_node_ids)
            out.header.receiver_id = initiator_id;

        (void)_hub.send(out);
    }

    template<typename Packet, typename Hub, typename Manager>
    void external_channel<Packet, Hub, Manager>::on_result(
        std::uint8_t initiator_id,
        task_uid_t uid,
        etools::memory::buffer<>&& result,
        status_code code)
    {
        send_reply(uid, code, etools::memory::buffer_view{result.data(), result.size()}, initiator_id);
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

        if (code != status_code::ok)
            send_reply(req.uid(), code, etools::memory::buffer_view{nullptr, 0}, initiator_id);
    }

} // namespace etask::core::channels

#endif // ETASK_CORE_CHANNELS_EXTERNAL_CHANNEL_TPP_
