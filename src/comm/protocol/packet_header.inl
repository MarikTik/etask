/**
* @file packet_header.inl
*
* @brief implementation of packet_header methods.
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
*
* @par Changelog
* - 2025-07-03 Initial creation.
* - 2025-07-14 Added `noexcept` specifier to methods for better exception safety.
* - 2025-07-15 Renamed `header_t` to `packet_header` for clarity.
*/
#ifndef ETASK_COMM_PROTOCOL_PACKET_HEADER_INL_
#define ETASK_COMM_PROTOCOL_PACKET_HEADER_INL_
#include "packet_header.hpp"

namespace etask::comm::protocol{

    inline packet_header::packet_header(uint16_t raw_value, uint8_t sender_id) noexcept
        : _space{raw_value}, _sender_id{sender_id}
    {
    }

    inline packet_header::packet_header(uint8_t type, uint8_t version, bool encrypted, bool fragmented, uint8_t priority, flags_t flags, bool validated, bool reserved, uint8_t sender_id) noexcept
        : _space{static_cast<uint16_t>(
              (static_cast<uint16_t>(type & 0xF) << 12) |
              (static_cast<uint16_t>(version & 0x3) << 10) |
              ((static_cast<uint16_t>(encrypted) & 0x1) << 9) |
              ((static_cast<uint16_t>(fragmented) & 0x1) << 8) |
              (static_cast<uint16_t>(priority & 0x7) << 5) |
              (static_cast<uint16_t>(static_cast<uint8_t>(flags) & 0x7) << 2) |
              ((static_cast<uint16_t>(validated) & 0x1) << 1) |
              ((static_cast<uint16_t>(reserved) & 0x1)))},
          _sender_id{sender_id}
    {
    }
    
    inline uint8_t packet_header::type() const noexcept{
        return (_space >> 12) & 0xF;
    }
    
    inline uint8_t packet_header::version() const noexcept{
        return (_space >> 10) & 0x3; 
    }
    
    inline bool packet_header::encrypted() const noexcept{
        return (_space & 0x0200) != 0; 
    }
    
    inline bool packet_header::fragmented() const noexcept{ 
        return (_space & 0x0100) != 0; 
    }
    
    inline uint8_t packet_header::priority() const noexcept{ 
        return (_space >> 5) & 0x7; 
    }
    
    inline flags_t packet_header::flags() const noexcept {
        return static_cast<flags_t>((_space >> 2) & 0x7);
    }
    
    inline bool packet_header::validated() const noexcept
    {
        return (_space & 0x0002) != 0;
    }
    
    inline bool packet_header::reserved() const noexcept
    {
        return (_space & 0x0001) != 0;
    }

    inline uint8_t packet_header::sender_id() const noexcept
    {
        return _sender_id;
    }

}

#endif // ETASK_COMM_PROTOCOL_PACKET_HEADER_INL_