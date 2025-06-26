#ifndef COMM_WIFI_INTERFACE_TPP_
#define COMM_WIFI_INTERFACE_TPP_

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
    std::optional<Packet> wifi_interface<tag>::try_receive() {
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
    void wifi_interface<tag>::send(Packet& packet) {
        
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
#endif // COMM_WIFI_INTERFACE_TPP_
