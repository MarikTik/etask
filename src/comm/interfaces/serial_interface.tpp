#ifndef COMM_SERIAL_INTERFACE_TPP_
#define COMM_SERIAL_INTERFACE_TPP_
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

}

#endif // ARDUINO
#endif // COMM_SERIAL_INTERFACE_TPP_