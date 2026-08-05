/**
* @file router.hpp
*
* @brief How arriving packets are routed - the node's inbound dispatch.
*
* @note User-owned config, and the inbound half of external comms. Include and
*       use this only once you have defined a transport and an `external_channel`
*       (see config/wiring.hpp) - it references both. A node with no external
*       comms does not use this file at all.
*
* This is the one place that decides what happens to a packet the moment it
* arrives. The default routes etask command packets to the task manager (via
* `external_channel::dispatch`), but a handler can do anything - the router is
* just "a packet of type X arrived -> run this".
*
* ## The model
*
* `ecomm::router` polls one or more transport channels and, for each packet that
* arrives, calls the handler whose parameter type matches it. The packet types
* it watches for are read off the handlers themselves - you never name a type
* twice. One `on_channel(channel, handlers...)` group per channel; drain it each
* tick with `try_receive_any()`. It owns per-channel reassembly state, so it
* must persist across polls (the single `inline` instance below), driven from
* `app::loop()`.
*/
#ifndef CONFIG_ROUTER_HPP_
#define CONFIG_ROUTER_HPP_
#include <ecomm/fabric/router.hpp>
#include "wiring.hpp"
// #include "../support/example_channel.hpp"   // your transport(s)

namespace config {

    /**
    * @brief The inbound router for this node.
    *
    * Watches `link` for `packet_t`s and hands each to the task manager via
    * `external_channel::dispatch`, which parses the etask request, runs the
    * requested manager operation, and sends any reply back through `link`.
    *
    * @note `link` and `external` are the instances you defined in wiring.hpp
    *       when enabling external comms.
    */
    inline auto router = ecomm::router{
        ecomm::on_channel(link,

            // --- default: etask command packets -> task manager ---
            [](packet_t& packet) {
                external.dispatch(packet);
            }

            // --- add your own packet types here ---
            // A handler is just `[](your_packet_t& p) { ... }`; the router polls
            // `link` for every packet type its handlers declare. For example:
            //
            //   , [](telemetry_packet_t& p) {
            //         // do anything - store it, forward it, ignore the manager entirely
            //     }
            //
            // (declare telemetry_packet_t alongside packet_t in protocol.hpp).
        )

        // --- add another link here ---
        // A second transport is a second on_channel(...) group, e.g.:
        //
        //   , ecomm::on_channel(wifi,
        //         [](packet_t& p) { external.dispatch(p); }
        //     )
    };

    /**
    * @brief Drain every packet ready on every routed channel this tick.
    *
    * Call once per `app::loop()`. Returns after the router has dispatched
    * everything currently framable; partially-arrived packets wait for the next
    * call.
    */
    inline void poll_inbound() {
        while (router.try_receive_any()) { }
    }

} // namespace config

#endif // CONFIG_ROUTER_HPP_
