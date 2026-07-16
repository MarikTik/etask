// SPDX-License-Identifier: MIT
/**
* @file reply.tpp
*
* @brief Definition of reply.hpp api.
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
#ifndef ETASK_CORE_PROTOCOL_REPLY_TPP_
#define ETASK_CORE_PROTOCOL_REPLY_TPP_
#include "reply.hpp"
#include <ecomm/protocol/header_type.hpp>
#include <ecomm/protocol/header_options.hpp>
#include <cstring>
#include <algorithm>

namespace etask::core::protocol {

    namespace detail {

        template<typename Packet, typename TaskUid>
        reply_base<Packet, TaskUid>::reply_base(TaskUid uid, status_code code, etools::memory::buffer_view result) noexcept
            : _uid{uid}, _code{code}, _result{result}
        {
        }

        template<typename Packet, typename TaskUid>
        Packet reply_base<Packet, TaskUid>::build() const noexcept
        {
            Packet out{
                ecomm::protocol::header_type::data,
                _code == status_code::ok ? ecomm::protocol::header_options::none : ecomm::protocol::header_options::error
            };

            std::size_t offset = 0;
            std::memcpy(out.payload + offset, &_uid, sizeof(_uid));
            offset += sizeof(_uid);
            std::memcpy(out.payload + offset, &_code, sizeof(_code));
            offset += sizeof(_code);

            const auto available = Packet::payload_size - offset;
            const auto copied = std::min(available, _result.size());
            // _result.data() is nullptr for an empty/default buffer_view; memcpy's
            // source argument must never be null, even with copied == 0.
            if (copied > 0)
                std::memcpy(out.payload + offset, _result.data(), copied);

            return out;
        }

    } // namespace detail

    template<typename Packet, typename TaskUid>
    reply<Packet, TaskUid, true>::reply(
        TaskUid uid, status_code code, etools::memory::buffer_view result, std::uint8_t receiver_id) noexcept
        : detail::reply_base<Packet, TaskUid>{uid, code, result}
        , _receiver_id{receiver_id}
    {
    }

    template<typename Packet, typename TaskUid>
    Packet reply<Packet, TaskUid, true>::to_packet() const noexcept
    {
        Packet out = this->build();
        out.header.receiver_id = _receiver_id; 
        // ECOMM_BOARD_ID is already set by default for sender_id
        return out;
    }

    template<typename Packet, typename TaskUid>
    Packet reply<Packet, TaskUid, false>::to_packet() const noexcept
    {
        return this->build();
    }

} // namespace etask::core::protocol
#endif // ETASK_CORE_PROTOCOL_REPLY_TPP_
