// SPDX-License-Identifier: MIT
/**
* @file request.tpp
*
* @brief Definition of request.hpp api.
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
#ifndef ETASK_CORE_PROTOCOL_REQUEST_TPP_
#define ETASK_CORE_PROTOCOL_REQUEST_TPP_
#include "request.hpp"
#include <cstring>

namespace etask::core::protocol {

    namespace detail {

        template<typename Packet, typename TaskUid>
        request_base<Packet, TaskUid>::request_base(const Packet& packet) noexcept
            : _packet{packet}
        {
        }

        template<typename Packet, typename TaskUid>
        directive::wire_command request_base<Packet, TaskUid>::command() const noexcept
        {
            std::byte raw;
            std::memcpy(&raw, _packet.payload, sizeof(raw));
            return directive{raw}.command();
        }

        template<typename Packet, typename TaskUid>
        completion_reason request_base<Packet, TaskUid>::reason() const noexcept
        {
            std::byte raw;
            std::memcpy(&raw, _packet.payload, sizeof(raw));
            return directive{raw}.reason();
        }

        template<typename Packet, typename TaskUid>
        TaskUid request_base<Packet, TaskUid>::uid() const noexcept
        {
            TaskUid uid;
            std::memcpy(&uid, _packet.payload + sizeof(std::byte), sizeof(uid));
            return uid;
        }

        template<typename Packet, typename TaskUid>
        etools::memory::buffer_view request_base<Packet, TaskUid>::args() const noexcept
        {
            constexpr std::size_t offset = sizeof(std::byte) + sizeof(TaskUid);
            return etools::memory::buffer_view{_packet.payload + offset, Packet::payload_size - offset};
        }

    } // namespace detail

    template<typename Packet, typename TaskUid>
    std::uint8_t request<Packet, TaskUid, true>::sender_id() const noexcept
    {
        return this->_packet.header.sender_id;
    }

} // namespace etask::core::protocol
#endif // ETASK_CORE_PROTOCOL_REQUEST_TPP_
