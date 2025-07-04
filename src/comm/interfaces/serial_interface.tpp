/**
* @file serial_interface.tpp
*
* @brief implementation of serial_interface.tpp methods.
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
#ifndef ETASK_COMM_SERIAL_INTERFACE_TPP_
#define ETASK_COMM_SERIAL_INTERFACE_TPP_
#ifdef ARDUINO
#include "../protocol/validator.hpp"

namespace etask::comm::interfaces {

    template<uint8_t tag>
    serial_interface<tag>::serial_interface(HardwareSerial &serial)
        : _serial{serial}
    {
    }
    template<uint8_t tag>
    template<typename Packet>
    inline std::optional<Packet> serial_interface<tag>::try_receive() {
        static_assert(std::is_trivially_copyable_v<Packet>, "Packet must be trivially copyable");
        constexpr std::size_t packet_size = sizeof(Packet);
        if (_serial.available() < packet_size) return std::nullopt;

        Packet packet;
        protocol::validator<Packet> validator; 
        _serial.readBytes(
            reinterpret_cast<std::uint8_t *>(&packet),
            packet_size
        );
        
        if (not validator.is_valid(packet)){
            //TODO Handle invalid packet
            return std::nullopt;
        }
        return packet;
    }

    template<uint8_t tag>
    template<typename Packet>
    void serial_interface<tag>::send(Packet &packet) {
        //TODO Implement validation pipeline to guarantee successful packet transmission
        static_assert(std::is_trivially_copyable_v<Packet>, "Packet must be trivially copyable");
        protocol::validator<Packet> validator;
        validator.seal(packet);
        _serial.write(reinterpret_cast<uint8_t*>(&packet), sizeof(Packet));
    }

} // namespace etask::comm::interfaces

#endif // ARDUINO
#endif // ETASK_COMM_SERIAL_INTERFACE_TPP_