// SPDX-License-Identifier: MIT
/**
* @file example_channel.hpp
*
* @brief Example transport channel - a byte link the node talks over.
*
* @note User-owned, and an EXAMPLE. `support/` is where software helpers live:
*       the code that links things together - transports, buffers, codecs - as
*       opposed to raw hardware drivers (those go in hal/). A transport straddles
*       the two; it lives here because what it *is* is a communication link. If
*       you would rather keep it next to the hardware it pokes, move it to hal/ -
*       the split is a suggestion, not a rule.
*
*       One header per channel, as many as you need (serial, TCP, radio, ...).
*       Adapt this, add siblings, or delete it if this node has no external link.
*
* ## What a channel is
*
* A transport is an `ecomm::channels::channel<Impl>` (CRTP). The base handles
* framing, validation and sealing; `Impl` supplies only the raw byte I/O. For a
* streaming link (UART, TCP byte stream) `Impl` provides three primitives:
* ```cpp
* template<typename Packet> void        do_send(const Packet& p) noexcept;        // write sizeof(Packet) bytes
* template<typename Packet> bool        do_try_receive(Packet& p) noexcept;       // read one whole framed packet
*                           std::size_t do_receive_raw(std::byte* dst, std::size_t max) noexcept; // raw bytes (used by ecomm::router)
* ```
*
* ## No channel is instantiated here on purpose
*
* Whether this node even has an external link is your decision - an internal-only
* node may have none, another may have several. So this file defines the channel
* *type* but creates no instance and forces no default. You create the instance
* where you wire it up (see config/wiring.hpp), e.g.:
* ```cpp
* inline support::example_channel link{ your_port_handle };
* ```
* and then hand it to `external_channel` and/or an `ecomm::router`.
*/
#ifndef SUPPORT_EXAMPLE_CHANNEL_HPP_
#define SUPPORT_EXAMPLE_CHANNEL_HPP_
#include <ecomm/channels/channel.hpp>
#include <cstddef>

namespace support {

    /**
    * @brief Example byte-link channel. Replace the three `do_*` bodies with your
    *        platform's real byte I/O (UART, socket, radio, ...).
    *
    * As written it neither sends nor receives (a no-op link), so the project
    * builds before any hardware exists; wire it to real bytes when ready.
    */
    class example_channel : public ecomm::channels::channel<example_channel> {
    public:
        /// @brief Write the packet's bytes to the medium. TODO: implement.
        template<typename Packet>
        void do_send(const Packet& /*packet*/) noexcept {
            // TODO: write sizeof(Packet) bytes of `packet` to your UART/socket.
        }

        /// @brief Read one complete framed packet, if available. TODO: implement.
        template<typename Packet>
        bool do_try_receive(Packet& /*packet*/) noexcept {
            // TODO: return true and fill `packet` when a full frame has arrived.
            return false;
        }

        /// @brief Pull up to `max` raw bytes into `dst` (used by the router). TODO: implement.
        std::size_t do_receive_raw(std::byte* /*dst*/, std::size_t /*max*/) noexcept {
            // TODO: read available bytes from your UART/socket into `dst`.
            return 0;
        }
    };

} // namespace support

#endif // SUPPORT_EXAMPLE_CHANNEL_HPP_
