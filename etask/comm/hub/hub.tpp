/**
* @file hub.tpp
*
* @brief implementation of hub.tpp methods.
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
#ifndef ETASK_COMM_HUB_HUB_TPP_
#define ETASK_COMM_HUB_HUB_TPP_
#include "hub.hpp"

namespace etask::comm
{
    template <typename Packet, typename... Interfaces>
    inline hub<Packet, Interfaces...>::hub(Interfaces &&...args)
        : _interfaces{std::forward<Interfaces>(args)...}
    {
        use_sender<Interfaces...>();
        use_receiver<Interfaces...>();
    }

    template <typename Packet, typename... Interfaces>
    template <typename Interface>
    inline void hub<Packet, Interfaces...>::use_sender()
    {
        _sender_statuses.template set<Interface>();
    }

    template <typename Packet, typename... Interfaces>
    template <typename Interface>
    inline void hub<Packet, Interfaces...>::use_receiver()
    {
        _receiver_statuses.template set<Interface>();
    }

    template <typename Packet, typename... Interfaces>
    template <typename Interface>
    inline void hub<Packet, Interfaces...>::remove_sender()
    {
        _sender_statuses.template reset<Interface>();
    }

    template <typename Packet, typename... Interfaces>
    template <typename Interface>
    inline void hub<Packet, Interfaces...>::remove_receiver()
    {
        _receiver_statuses.template reset<Interface>();
    }

    template <typename Packet, typename... Interfaces>
    inline void hub<Packet, Interfaces...>::send(Packet &packet)
    {
        std::apply(
            [this, &packet](auto&... interfaces) {
                (..., maybe_send<std::decay_t<decltype(interfaces)>>(interfaces, packet));
            },
            _interfaces
        );
    }

    template <typename Packet, typename... Interfaces>
    inline std::optional<Packet> hub<Packet, Interfaces...>::try_receive()
    {
        std::optional<Packet> result;

        std::apply([this, &result](auto&... interfaces) {
            (... || ([this, &result, &interfaces] {  
                using interface_t = std::decay_t<decltype(interfaces)>;
             
                auto maybe = maybe_try_receive<interface_t>(interfaces);
                if (maybe) {
                    result = std::move(maybe);
                    return true; // Return true to stop the fold expression (short-circuit)
                }
                return false; // Return false to continue to the next interface
            }()));
        }, _interfaces);
        return result;
    }

    template <typename Packet, typename... Interfaces>
    template <typename Interface>
    inline void hub<Packet, Interfaces...>::maybe_send(Interface &interface, Packet &packet)
    {
        if (_sender_statuses.template test<Interface>())
            interface.send(packet);
    }

    template <typename Packet, typename... Interfaces>
    template <typename Interface>
    inline std::optional<Packet> hub<Packet, Interfaces...>::maybe_try_receive(Interface &interface)
    {
        if (_receiver_statuses.template test<Interface>())
            return interface.try_receive();
        return std::nullopt;
    }
    
}

#endif // ETASK_COMM_HUB_TPP_