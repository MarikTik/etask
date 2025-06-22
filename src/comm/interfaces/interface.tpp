#ifndef COMM_INTERFACE_TPP_
#define COMM_INTERFACE_TPP_
#include "interface.hpp"

namespace etask::comm::interfaces {
    template<typename InterfaceImpl>
    template<typename Packet>
    inline std::optional<Packet> interface<InterfaceImpl>::try_receive() {
        return static_cast<InterfaceImpl*>(this)->try_receive(); // CRTP to call the derived class's try_receive method
    }

    template<typename InterfaceImpl>
    template<typename Packet>
    inline void interface<InterfaceImpl>::send(Packet &packet) {
        static_cast<InterfaceImpl*>(this)->send(packet); // CRTP to call the derived class's send method
    }
} // namespace etask::comm::interfaces

#endif // COMM_INTERFACE_TPP_