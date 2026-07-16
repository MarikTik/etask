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
    void external_channel<Packet, Hub, Manager>::on_result(
        std::uint8_t initiator_id,
        task_uid_t uid,
        etools::memory::buffer<>&& result,
        status_code code)
    {
        etools::memory::buffer_view result_view{result.data(), result.size()};

        if constexpr (Packet::header_t::has_node_ids) {
            protocol::reply<Packet, task_uid_t> rep{uid, code, result_view, initiator_id};
            auto out = rep.to_packet();
            (void)_hub.send(out);
        } else {
            protocol::reply<Packet, task_uid_t> rep{uid, code, result_view};
            auto out = rep.to_packet();
            (void)_hub.send(out);
        }
    }

    template<typename Packet, typename Hub, typename Manager>
    void external_channel<Packet, Hub, Manager>::update()
    {
        auto received = _hub.template try_receive<Packet>();
        if (not received)
            return;

        protocol::request<Packet, task_uid_t> req{*received};

        std::uint8_t initiator_id;
        if constexpr (Packet::header_t::has_node_ids) {
            initiator_id = req.sender_id();
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
            etools::memory::buffer_view empty{nullptr, 0};
            if constexpr (Packet::header_t::has_node_ids) {
                protocol::reply<Packet, task_uid_t> err{req.uid(), code, empty, initiator_id};
                auto out = err.to_packet();
                (void)_hub.send(out);
            } else {
                protocol::reply<Packet, task_uid_t> err{req.uid(), code, empty};
                auto out = err.to_packet();
                (void)_hub.send(out);
            }
        }
    }

} // namespace etask::core::channels

#endif // ETASK_CORE_CHANNELS_EXTERNAL_CHANNEL_TPP_
