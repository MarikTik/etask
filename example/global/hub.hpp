// SPDX-License-Identifier: BSL-1.1
/**
* @file global_hub.hpp
*
* @brief Application-level communication hub wiring.
*
* This header defines the global hub instance that coordinates communication
* in the etask system. The hub multiplexes/demultiplexes packets over one or
* more transport interfaces.
*
* @note Currently supported interfaces are:
*       - `arduino_wifi_interface` (Wi-Fi transport)
*       - `arduino_serial_interface` (UART/serial transport)
*
* Users are free to add additional interfaces by deriving from the CRTP base
* `etask::comm::interfaces::interface<>`. This allows integrating custom
* transports (e.g., Ethernet, CAN, radio) without modifying the hub itself.
*
* @note The user is not responsible for validating and sealing packets in their
*       custom implementations of interfaces. That work lies solely on 
*       `etask::comm::interfaces::interface<>` class.
*
* @example
* // Example with multiple interfaces:
* using hub_t = etask::comm::hub<
*     global::packet_t,
*     etask::comm::interfaces::arduino_serial_interface,
*     etask::comm::interfaces::arduino_wifi_interface
* >;
* inline hub_t hub{etask::comm::interfaces::arduino_serial_interface{}, 
*                  etask::comm::interfaces::arduino_wifi_interface{}};
*
* @author
* Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-08-10
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef GLOBAL_HUB_HPP_
#define GLOBAL_HUB_HPP_
#include <etask/comm/hub/hub.hpp>
#include <etask/comm/interfaces/interfaces.hpp>
#include "protocol.hpp"


/**
* @class sample_interface
*
* @brief Example user-defined communication interface.
*
* Demonstrates how to implement a custom interface by inheriting from
* `etask::comm::interfaces::interface<Derived>`. Users should override
* `delegate_try_receive()` and `delegate_send()` with real transport logic.
*
* @note This is only a placeholder. Replace it with a custom interface implementation if needed.
*/
class sample_interface : public etask::comm::interfaces::interface<sample_interface> {
public:
    /**
    * @brief Attempt to receive a packet from the underlying transport.
    * 
    * @return A packet if available, otherwise std::nullopt.
    */
    template<typename Packet>
    std::optional<Packet> delegate_try_receive() {
        // Implement receiving logic here
        return std::nullopt; // Placeholder
    }

    /**
    * @brief Send a packet over the underlying transport.
    * 
    * @param packet Packet to send.
    */
    template<typename Packet>
    void delegate_send([[maybe_unused]] Packet &packet) {
        // Implement sending logic here
    }
};

namespace global{

    /**
    * @brief Global communication hub instance.
    *
    * This hub is used to manage communication between different components
    * of the etask system. Currently configured to use a Wi-Fi interface only, but can 
    * be extended to support other interfaces to fit user customization needs.
    *
    * @note This hub is a singleton instance that should be used throughout the application
    *       to ensure consistent communication handling.
    *
    * @see etask::comm::interfaces for interfaces supported by etask.
    */
    inline etask::comm::hub<packet_t, sample_interface> hub{sample_interface{}};

} // namespace global

#endif // GLOBAL_HUB_HPP_