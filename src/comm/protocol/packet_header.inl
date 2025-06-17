#ifndef PROTOCOL_PACKET_HEADER_INL_
#define PROTOCOL_PACKET_HEADER_INL_
#include "packet_header.hpp"
namespace etask::comm{
    inline header_t::header_t(uint16_t raw_value)
    :  _space{raw_value}
    {
    }
    
    inline header_t::header_t(uint8_t type, uint8_t version, bool encrypted, bool fragmented, uint8_t priority, flags_t flags, bool validated, bool reserved)
        : _space{static_cast<uint16_t>(
            (static_cast<uint16_t>(type & 0xF) << 12) |
            (static_cast<uint16_t>(version & 0x3) << 10) |
            ((static_cast<uint16_t>(encrypted) & 0x1) << 9) |
            ((static_cast<uint16_t>(fragmented) & 0x1) << 8) |
            (static_cast<uint16_t>(priority & 0x7) << 5) |
            (static_cast<uint16_t>(static_cast<uint8_t>(flags) & 0x7) << 2) |
            ((static_cast<uint16_t>(validated) & 0x1) << 1) |
            ((static_cast<uint16_t>(reserved) & 0x1))
        )}
    {
    }
    
    inline uint8_t header_t::type() const {
        return (_space >> 12) & 0xF;
    }
    
    inline uint8_t header_t::version() const {
        return (_space >> 10) & 0x3; 
    }
    
    inline bool header_t::encrypted() const {
        return (_space & 0x0200) != 0; 
    }
    
    inline bool header_t::fragmented() const { 
        return (_space & 0x0100) != 0; 
    }
    
    inline uint8_t header_t::priority() const{ 
        return (_space >> 5) & 0x7; 
    }
    
    inline flags_t header_t::flags() const {
        return static_cast<flags_t>((_space >> 2) & 0x7);
    }
    
    inline bool header_t::validated() const
    {
        return (_space & 0x0002) != 0;
    }
    
    inline bool header_t::reserved() const
    {
        return (_space & 0x0001) != 0;
    }
    
    inline uint16_t header_t::raw() const
    {
        return _space;
    }
}

#endif // PROTOCOL_PACKET_HEADER_INL_