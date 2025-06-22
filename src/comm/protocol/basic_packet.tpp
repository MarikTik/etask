#ifndef PROTOCOL_BASIC_PACKET_TPP_
#define PROTOCOL_BASIC_PACKET_TPP_
#include "basic_packet.hpp"
#include <cassert>
#include <algorithm>
namespace etask::comm::protocol {
    template <std::size_t PacketSize, typename TaskID_UnderlyingType>
    inline basic_packet<PacketSize, TaskID_UnderlyingType>::basic_packet(header_t header_param, TaskID_UnderlyingType task_id_param)
        : header{header_param}, task_id{task_id_param} 
    {
    }
    
    template <std::size_t PacketSize, typename TaskID_UnderlyingType>
    inline basic_packet<PacketSize, TaskID_UnderlyingType>::basic_packet(header_t header_param, TaskID_UnderlyingType task_id_param, const std::byte *payload_param, size_t payload_size_param)
        : basic_packet(header_param, task_id_param)
    {
        assert(payload_size_param <= payload_size && "Payload size exceeds packet capacity");
        if (payload_param and payload_size_param > 0) 
            std::copy(payload_param, payload_param + payload_size_param, payload);
    }
} // namespace etask::comm::protocol

#endif // PROTOCOL_BASIC_PACKET_TPP_