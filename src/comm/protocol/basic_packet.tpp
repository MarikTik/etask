/**
* @file basic_packet.tpp
*
* @brief implementation of basic_packet.tpp methods.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-03
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_COMM_PROTOCOL_BASIC_PACKET_TPP_
#define ETASK_COMM_PROTOCOL_BASIC_PACKET_TPP_
#include "basic_packet.hpp"
#include <cassert>
#include <algorithm>

namespace etask::comm::protocol {

    template <std::size_t PacketSize, typename TaskID_UnderlyingType>
    inline basic_packet<PacketSize, TaskID_UnderlyingType>::basic_packet(header_t header_param, TaskID_UnderlyingType task_id_param, uint8_t status_code_param)
        : header{header_param}, status_code{status_code_param}, task_id{task_id_param}
    {
    }
    
    template <std::size_t PacketSize, typename TaskID_UnderlyingType>
    inline basic_packet<PacketSize, TaskID_UnderlyingType>::basic_packet(header_t header_param, TaskID_UnderlyingType task_id_param, uint8_t status_code_param, const std::byte *payload_param, size_t payload_size_param)
        : basic_packet(header_param, task_id_param, status_code_param)
    {
        assert(payload_size_param <= payload_size && "Payload size exceeds packet capacity");
        if (payload_param and payload_size_param > 0) 
            std::copy(payload_param, payload_param + payload_size_param, payload);
    }
    
} // namespace etask::comm::protocol

#endif // ETASK_COMM_PROTOCOL_BASIC_PACKET_TPP_