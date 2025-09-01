// SPDX-License-Identifier: BSL-1.1
/**
* @file internal_channel.cpp
*
* @brief Definition of internal_channel.hpp api.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-08-14
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#include "internal_channel.hpp"
#include "../global/task_manager.hpp"
 
namespace channels{
    void internal_channel::on_result(
        [[maybe_unused]] uint8_t initiator_id,
        [[maybe_unused]] global::task_id uid,
        [[maybe_unused]] etools::memory::envelope<> &&result,
        [[maybe_unused]] etask::system::status_code code)
    {
    }

    etask::system::status_code internal_channel::pause_task(global::task_id uid)
    {
        return global::task_manager.pause_task(uid);
    }

    etask::system::status_code internal_channel::resume_task(global::task_id uid)
    {
        return global::task_manager.resume_task(uid);
    }

    etask::system::status_code internal_channel::abort_task(global::task_id uid)
    {
        return global::task_manager.abort_task(uid);
    }

} // namespace channels