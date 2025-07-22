/**
* @file interface.tpp
*
* @brief implementation of interface.tpp methods.
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
*      - Renamed implementation method of `InterfaceImpl` to `delegate_try_receive` and `delegate_send`.
* - 2025-07-18
*      - Disabled acceptance of packets not intended for this board.
* - 2025-07-21
*      - Corrected template argument deduction for `try_receive`.

*/
#ifndef ETASK_COMM_INTERFACE_TPP_
#define ETASK_COMM_INTERFACE_TPP_
#include "interface.hpp"
#include "../protocol/protocol.hpp"
namespace etask::comm::interfaces {
    
    template<typename InterfaceImpl>
    template<typename Packet>
    inline std::optional<Packet> interface<InterfaceImpl>::try_receive() {
        auto packet = static_cast<InterfaceImpl*>(this)->template delegate_try_receive<Packet>();    // CRTP to call the derived class's try_receive method
        if (packet and packet->header.receiver_id == ETASK_BOARD_ID) return packet; // Only return packets intended for this board
        return std::nullopt;
    }

    template<typename InterfaceImpl>
    template<typename Packet>
    inline void interface<InterfaceImpl>::send(Packet &packet) {
        static_cast<InterfaceImpl*>(this)->delegate_send(packet); // CRTP to call the derived class's send method
    }

} // namespace etask::comm::interfaces

#endif // ETASK_COMM_INTERFACE_TPP_