/**
* @file serial_interface.hpp
* @brief Defines a serial communication interface for packet-based task dispatching on Arduino platforms.
*
* This file provides the declaration of the `serial_interface` class, a CRTP-based implementation
* of a communication interface that enables reliable packet exchange via serial communication,
* typically used on Arduino-compatible boards.
*
* The interface is templated with a `tag` parameter for distinguishing between multiple serial interfaces
* and inherits from the generic `interface<Derived>` base class to provide `send()` and `try_receive()` methods
* for any fixed-size packet structure. Packets are validated using the `validator` mechanism defined
* in the protocol layer before being accepted or transmitted.
*
* This implementation assumes that packets are received and sent as fixed-size binary blobs, and that
* checksum validation or sealing is performed transparently. It is designed for environments
* where low-latency, reliable task communication over UART is required.
*
* @note This file is only compiled when targeting platforms with the `ARDUINO` macro defined.
*       Specifically, it depends on `HardwareSerial` being available.
*
* @see interface.hpp
* @see validator.hpp
*/

#ifndef COMM_SERIAL_INTERFACE_HPP_
#define COMM_SERIAL_INTERFACE_HPP_
#ifdef ARDUINO
#include "interface.hpp"
#include <HardwareSerial.h>
#include <cstdint>
namespace etask::comm::interfaces {
    /**
    * @class serial_interface
    * @brief Serial communication interface for ESP32.
    *
    * This class provides a serial communication interface for the ESP32 platform.
    * It inherits from the `scr::comm::interface` base class and implements the
    * `try_receive` and `send` methods for serial communication.
    *
    * @tparam tag The tag used to identify the interface type (default is 0) in case the Serial instance passed varies (e.g. Serial1, Serial2 ...).
    * 
    * @warning Using multiple serial interfaces with the same tag may lead to unexpected behavior.
    */
    template<std::uint8_t tag = 0>
    class serial_interface : public interface<serial_interface<tag>>
    {
    public:
        /**
        * @brief Constructs a serial interface with the specified serial port.
        *
        * @param serial The reference to the HardwareSerial object to use for communication.
        */
        serial_interface(HardwareSerial &serial);

        /**
        * @brief Attempts to receive a packet from the serial port.
        *
        * This method reads data from the serial port and attempts to construct
        * a packet. If a complete packet is received, it is returned; otherwise,
        * std::nullopt is returned.
        *
        * @tparam Packet The type of packet to attempt receiving.
        * 
        * @return An optional packet if successfully received, or std::nullopt if not.
        */
        template<typename Packet>
        inline std::optional<Packet> try_receive();

        /**
        * @brief Sends a packet over the serial port.
        *
        * This method sends the specified packet over the serial port.
        *
        * @param packet The reference of the packet to send.
        * 
        * @tparam Packet The type of packet to send.
        * 
        * @note The packet's crc32 field is expected to exist and will be altered during 
        * the transmission process.
        * @note The caller must not assume that the packet remains bitwise identical after sending.
        */
        template<typename Packet>
        inline void send(Packet &packet);
    private:
        HardwareSerial &_serial; ///< Reference to the HardwareSerial object for communication.
    };
}
#include "serial_interface.tpp"
#endif // ARDUINO
#endif // COMM_SERIAL_INTERFACE_HPP_