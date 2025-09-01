// SPDX-License-Identifier: BSL-1.1
/**
* @file internal_channel.tpp
*
* @brief Definition of internal_channel.hpp template api.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-08-31
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef CHANNELS_INTERNAL_CHANNEL_TPP_
#define CHANNELS_INTERNAL_CHANNEL_TPP_
#include "internal_channel.hpp"
#include "../global/task_manager.hpp"
#include <etask/comm/protocol/config.hpp>

namespace channels{
    template <typename... Args>
    inline etask::system::status_code internal_channel::register_task(global::task_id uid, Args&&... args)
    {
        return global::task_manager.register_task(
            this, 
            ETASK_BOARD_ID,
            uid,
            std::forward<Args>(args)...
        );
    }
}

#endif // CHANNELS_INTERNAL_CHANNEL_TPP_