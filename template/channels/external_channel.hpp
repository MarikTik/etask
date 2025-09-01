// SPDX-License-Identifier: BSL-1.1
/**
* @file external_channel.hpp
* @brief Defines a channel for connecting externally arriving packets to the task manager.
*
* The `external_channel` bridges incoming and outgoing communication between
* the etask system and external transport layers (UART, TCP, etc.).
* 
* #### Responsibilities:
* - Receive packets from the global hub and translate them into task manager operations.
* - Forward results produced by tasks back to the hub, encapsulated in protocol packets.
*
* @note It is not advised to change this file directly. If you need to change the implementation
*       feel free to do so in external_channel.cpp
*
* @see channels.hpp for the aggregated include
* @see etask::system::channel for the abstract base interface
*
* @section customization Customization
* - See @ref extchan_register_forwarding to change how arguments are forwarded
*   to task_manager::register_task.
*
*   @snippet external_channel.cpp extchan.register_forwarding
*
* - See @ref extchan_error_reply to customize error replies.
*
*   @snippet external_channel.cpp extchan.error_reply
* 
* @date 2025-07-15
*
* @author Mark Tikhonov
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef CHANNELS_EXTERNAL_CHANNEL_HPP_
#define CHANNELS_EXTERNAL_CHANNEL_HPP_
#include <etask/system/channel.hpp>
#include <etools/memory/envelope.hpp>
#include "../global/task_id.hpp"

namespace channels{

    /**
    * @struct external_channel
    * 
    * @brief Communication channel for handling externally sourced packets.
    *
    * The external channel is responsible for bridging data between the
    * global protocol hub and the etask task manager. It receives commands
    * (register, pause, resume, abort) from incoming packets and forwards
    * results back to the external system as protocol packets.
    *
    * #### Typical usage:
    * 
    * - Call `update()` periodically to poll the hub for new packets.
    * 
    * - Implement application-specific logic for sending/receiving at the hub layer.
    *
    * @note This channel is primarily intended for integrating external communication
    *       mediums such as UART, CAN, or network sockets.
    */
    struct external_channel : public etask::system::channel<global::task_id> {

        /**
        * @brief Deliver task results back to the external system.
        *
        * Called by the task manager when a task completes or is interrupted.
        * Wraps the result and status code into a protocol packet and sends
        * it through the global hub.
        *
        * @param initiator_id ID of the original requester of the task.
        * @param uid Unique identifier of the task that produced the result.
        * @param result Result payload produced by the task (moved).
        * @param code Status code representing the outcome of the task.
        */
        void on_result(
            uint8_t initiator_id,
            global::task_id uid,
            etools::memory::envelope<> &&result,
            etask::system::status_code code
        ) override;

        /**
        * @brief Poll for externally arriving packets and dispatch them to the task manager.
        *
        * The update routine checks the global hub for received packets and interprets
        * their headers:
        * - If no flags are set, the packet is treated as a request to register a new task.
        * - If the abort, pause, or resume flags are set, the corresponding operation
        *   is invoked on the task manager.
        * - If an error occurs (unknown task, bad parameters, etc.), an error packet is
        *   generated and sent back to the requester.
        *
        * @note This method should be invoked periodically from the main loop of the
        *       application to ensure timely handling of external commands.
        */
        void update();
    };

} // namespace channels

namespace global{
    /**
    * @brief Global instance of the external channel, used as the default origin
    * for tasks invoked outside the system (externally).
    */
    inline channels::external_channel external_channel;
} // namespace global

#endif // CHANNELS_EXTERNAL_CHANNEL_HPP_