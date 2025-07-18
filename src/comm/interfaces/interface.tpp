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
*      - renamed implementation method of `IntrefaceImpl` to `delegate_try_receive` and `delegate_send`.
*/
#ifndef ETASK_COMM_INTERFACE_TPP_
#define ETASK_COMM_INTERFACE_TPP_
#include "interface.hpp"

namespace etask::comm::interfaces {
    
    template<typename InterfaceImpl>
    template<typename Packet>
    inline std::optional<Packet> interface<InterfaceImpl>::try_receive() {
        return static_cast<InterfaceImpl*>(this)->delegate_try_receive(); // CRTP to call the derived class's try_receive method
    }

    template<typename InterfaceImpl>
    template<typename Packet>
    inline void interface<InterfaceImpl>::send(Packet &packet) {
        static_cast<InterfaceImpl*>(this)->delegate_send(packet); // CRTP to call the derived class's send method
    }

} // namespace etask::comm::interfaces

#endif // ETASK_COMM_INTERFACE_TPP_