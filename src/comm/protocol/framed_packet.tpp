/**
* @file framed_packet.tpp
*
* @brief implementation of framed_packet.tpp methods.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-15
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_COMM_PROTOCOL_FRAMED_PACKET_TPP_
#define ETASK_COMM_PROTOCOL_FRAMED_PACKET_TPP_
#include "framed_packet.hpp"
#include <cassert>
namespace etask::comm::protocol {

    
    template <std::size_t PacketSize, typename TaskID_UnderlyingType, typename ChecksumPolicy>
    inline framed_packet<PacketSize, TaskID_UnderlyingType, ChecksumPolicy>::framed_packet(header_t header_param, TaskID_UnderlyingType task_id_param, uint8_t status_code_param) noexcept
        : header{header_param}, status_code{status_code_param}, task_id{task_id_param}
    {
    }

    template <std::size_t PacketSize, typename TaskID_UnderlyingType, typename ChecksumPolicy>
    inline framed_packet<PacketSize, TaskID_UnderlyingType, ChecksumPolicy>::framed_packet(
        header_t header_param, TaskID_UnderlyingType task_id_param, uint8_t status_code_param, const std::byte *payload_param, size_t payload_size_param) noexcept
        : header{header_param}, status_code{status_code_param}, task_id{task_id_param}
    {
        assert(payload_size_param <= payload_size && "Payload size exceeds packet capacity");
        if (payload_param && payload_size_param > 0) std::memcpy(payload, payload_param, payload_size_param);
    }
} // namespace etask::comm::protocol
#endif // ETASK_COMM_PROTOCOL_FRAMED_PACKET_TPP_