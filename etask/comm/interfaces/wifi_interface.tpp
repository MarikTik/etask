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
*/
#ifndef ETASK_COMM_WIFI_INTERFACE_TPP_
#define ETASK_COMM_WIFI_INTERFACE_TPP_
#ifndef COMM_NO_WIFI_SUPPORT
#include "wifi_interface.hpp"
#include "../protocol/validator.hpp"

namespace etask::comm::interfaces {

    template<uint8_t tag>
    wifi_interface<tag>::wifi_interface(WiFiServer& server) 
        : _server(server) 
    {
    }

    template<uint8_t tag>
    template<typename Packet>
    std::optional<Packet> wifi_interface<tag>::delegate_try_receive() {
        if (not _client) {
            _client = _server.available();
            if (not _client) return std::nullopt;
        }

        if (_client.available() < sizeof(Packet)) return std::nullopt;

        Packet packet;
        protocol::validator<Packet> validator;
        _client.read(reinterpret_cast<uint8_t*>(&packet), sizeof(Packet));

        if (not validator.is_valid(packet)) {
            // Optionally, flush or drop client if corruption is persistent
            return std::nullopt;
        }
        return packet;
    }

    template<uint8_t tag>
    template<typename Packet>
    void wifi_interface<tag>::delegate_send(Packet& packet) {
        
        if (not _client) {
            _client = _server.available();
            if (not _client) return;
        }

        protocol::validator<Packet> validator;
        validator.seal(packet);
        _client.write(reinterpret_cast<uint8_t*>(&packet), sizeof(Packet));
    }

} // namespace etask::comm::interfaces

#endif // COMM_NO_WIFI_SUPPORT
#endif // ETASK_COMM_WIFI_INTERFACE_TPP_
