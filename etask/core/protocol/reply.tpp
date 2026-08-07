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

namespace etask::core::protocol {

    template<typename Packet, typename TaskUid>
    Packet reply<Packet, TaskUid>::make(TaskUid uid, status_code code) noexcept
    {
        Packet out{
            ecomm::protocol::header_type::data,
            code == status_code::ok ? ecomm::protocol::header_options::none : ecomm::protocol::header_options::error
        };

        std::memcpy(out.payload, &uid, sizeof(uid));
        std::memcpy(out.payload + sizeof(uid), &code, sizeof(code));
        // The result region (out.payload + result_offset ..) stays zero-filled;
        // a concluding task's outcome packs into it in place, or a rejection sends
        // it empty.
        return out;
    }

} // namespace etask::core::protocol
#endif // ETASK_CORE_PROTOCOL_REPLY_TPP_
