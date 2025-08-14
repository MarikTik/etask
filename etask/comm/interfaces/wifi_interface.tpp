// SPDX-License-Identifier: BSL-1.1
/**
* @file wifi_interface.tpp
*
* @brief implementation of wifi_interface.tpp methods.
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
* - 2025-07-03 
*      - Initial creation.
* - 2025-07-17
*      - renamed `try_receive` and `send` methods to `delegate_try_receive` and `delegate_send` respectively to
*        enable CRTP delegation via base `interface<>` class.
* - 2024-08-12
*      - Moved validation details to `interface` base.
*/
#ifndef ETASK_COMM_WIFI_INTERFACE_TPP_
#define ETASK_COMM_WIFI_INTERFACE_TPP_
#ifndef COMM_NO_WIFI_SUPPORT
#include "wifi_interface.hpp"

namespace etask::comm::interfaces {

    template<uint8_t tag>
    wifi_interface<tag>::wifi_interface(WiFiServer& server) 
        : _server(server) 
    {
    }

    template<uint8_t tag>
    template<typename Packet>
    inline std::optional<Packet> wifi_interface<tag>::delegate_try_receive() {
        if (not _client) {
            _client = _server.available();
            if (not _client) return std::nullopt;
        }

        if (_client.available() < sizeof(Packet)) return std::nullopt;

        _client.read(reinterpret_cast<uint8_t*>(&packet), sizeof(Packet));  
        return packet;
    }

    template<uint8_t tag>
    template<typename Packet>
    inline void wifi_interface<tag>::delegate_send(Packet& packet) {
        
        if (not _client) {
            _client = _server.available();
            if (not _client) return;
        }
        _client.write(reinterpret_cast<uint8_t*>(&packet), sizeof(Packet));
    }

} // namespace etask::comm::interfaces

#endif // COMM_NO_WIFI_SUPPORT
#endif // ETASK_COMM_WIFI_INTERFACE_TPP_
