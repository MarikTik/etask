// SPDX-License-Identifier: BSL-1.1
/**
* @file external_channel.cpp
*
* @brief Definition of external_channel.hpp api.
*
* @section customization_points Customization points
* - @ref extchan_register_forwarding  — change arguments forwarded to task_manager::register_task
* - @ref extchan_error_reply          — change how error packets are formed/sent
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-08-10
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#include "external_channel.hpp"
#include "../global/task_manager.hpp"
#include "../global/hub.hpp"
#include "../global/protocol.hpp"
#include <etask/comm/protocol/config.hpp>
#include <etools/meta/info_gen.hpp>
#include <etools/memory/envelope_view.hpp>
generate_has_member_variable(fcs);

namespace channels {
    void external_channel::on_result(
        uint8_t initiator_id,
        global::task_id uid,
        etools::memory::envelope<> &&result,
        etask::system::status_code code
    ) 
    {
        etask::comm::protocol::packet_header header{
            etask::comm::protocol::header_type::data,
            false, // encrypted
            false, // fragmented
            0,     // priority
            etask::comm::protocol::header_flags::none, // flags
            etools::meta::has_member_variable_fcs_v<global::packet_t>, // validated
            0, // reserved
            initiator_id // receiver_id
        };
        global::packet_t packet{
            header,
            uid,
            code,
            result.data(),
            result.size()
        };
        global::hub.send(packet);
    }
    void external_channel::update() {
        auto packet = global::hub.try_receive();

        if (not packet) return;
        
        const auto header = packet->header;
        const auto flags = header.flags();
        const auto iid = header.sender_id();
        const auto uid = packet->task_id;

        etask::system::status_code code;

        if (flags == etask::comm::protocol::header_flags::none){
            const auto sender_id = header.sender_id();    
            const auto params = etools::memory::envelope_view{
                packet->payload,
                global::packet_t::payload_size
            };
            
            /// @todo Adjust forwarded arguments to register_task for your app if needed.

            /// \anchor extchan_register_forwarding
            /// Customization Point: register_task argument forwarding.
            /// You can change the types and number of arguments here after uid; they will be
            /// perfectly forwarded into the selected task's constructor.
            //! [extchan.register_forwarding]
            code = global::task_manager.register_task(
                this,       // channel
                sender_id,  // initiator id
                uid,        // task id
                params      // constructor args: adjust/add/remove as needed
            );
            //! [extchan.register_forwarding]
        }
        else if (flags == etask::comm::protocol::header_flags::abort){
            code = global::task_manager.abort_task(uid);
        }
        else if (flags == etask::comm::protocol::header_flags::pause){
            code = global::task_manager.pause_task(uid);
        }
        else if (flags == etask::comm::protocol::header_flags::resume){
            code = global::task_manager.resume_task(uid);
        }

        if (code not_eq etask::system::status_code::ok){

            /// \anchor extchan_error_reply
            /// Customization Point: error reply formatting / transport behavior.
            //! [extchan.error_reply]
            etask::comm::protocol::packet_header header{
                etask::comm::protocol::header_type::data,
                false, // encrypted
                false, // fragmented
                0,     // priority
                etask::comm::protocol::header_flags::error, // flags
                etools::meta::has_member_variable_fcs_v<global::packet_t>, // validated
                0, // reserved
                iid // receiver_id
            };
            //! [extchan.error_reply]

            global::packet_t packet{
                header,
                uid,
                code
            };

            global::hub.send(packet);
        }
    }
} // namespace channels