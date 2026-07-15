// SPDX-License-Identifier: BSL-1.1
/**
* @file internal_channel.tpp
*
* @brief Definition of internal_channel.hpp api.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-07-13
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_INTERNAL_CHANNEL_TPP_
#define ETASK_CORE_INTERNAL_CHANNEL_TPP_
#include "internal_channel.hpp"

namespace etask::core {

    template<typename Manager>
    internal_channel<Manager>::internal_channel(Manager& manager) noexcept
        : _manager{manager}
    {
    }

    template<typename Manager>
    void internal_channel<Manager>::on_result(
        [[maybe_unused]] std::uint8_t initiator_id,
        [[maybe_unused]] task_uid_t uid,
        [[maybe_unused]] etools::memory::buffer<>&& result,
        [[maybe_unused]] status_code code)
    {
    }

    template<typename Manager>
    template<typename... Args>
    status_code internal_channel<Manager>::register_task(task_uid_t uid, Args&&... args)
    {
        return _manager.register_task(this, ECOMM_BOARD_ID, uid, std::forward<Args>(args)...);
    }

    template<typename Manager>
    status_code internal_channel<Manager>::pause_task(task_uid_t uid)
    {
        return _manager.pause_task(uid);
    }

    template<typename Manager>
    status_code internal_channel<Manager>::resume_task(task_uid_t uid)
    {
        return _manager.resume_task(uid);
    }

    template<typename Manager>
    status_code internal_channel<Manager>::complete_task(task_uid_t uid, completion_reason reason)
    {
        return _manager.complete_task(uid, reason);
    }

} // namespace etask::core

#endif // ETASK_CORE_INTERNAL_CHANNEL_TPP_
