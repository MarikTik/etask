// SPDX-License-Identifier: MIT
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
* MIT License
* Copyright (c) 2025 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_CHANNELS_INTERNAL_CHANNEL_TPP_
#define ETASK_CORE_CHANNELS_INTERNAL_CHANNEL_TPP_
#include "internal_channel.hpp"

namespace etask::core::channels {

    template<typename Manager, std::size_t ScratchBytes>
    internal_channel<Manager, ScratchBytes>::internal_channel(Manager& manager) noexcept
        : _manager{manager}
    {
    }

    template<typename Manager, std::size_t ScratchBytes>
    void internal_channel<Manager, ScratchBytes>::complete(
        [[maybe_unused]] std::uint8_t initiator_id,
        [[maybe_unused]] task_uid_t uid,
        [[maybe_unused]] status_code code,
        completion_reason reason,
        task<task_uid_t>& t)
    {
        // Run on_complete against a discard region so the task's `return {...}`
        // behaves identically to a wire task; the packed bytes are never read.
        detail::result_region_scope region{_scratch.data(), _scratch.size()};
        (void)t.on_complete(reason);
    }

    template<typename Manager, std::size_t ScratchBytes>
    template<typename... Args>
    status_code internal_channel<Manager, ScratchBytes>::register_task(task_uid_t uid, Args&&... args)
    {
        return _manager.register_task(this, ECOMM_BOARD_ID, uid, std::forward<Args>(args)...);
    }

    template<typename Manager, std::size_t ScratchBytes>
    status_code internal_channel<Manager, ScratchBytes>::pause_task(task_uid_t uid)
    {
        return _manager.pause_task(uid);
    }

    template<typename Manager, std::size_t ScratchBytes>
    status_code internal_channel<Manager, ScratchBytes>::resume_task(task_uid_t uid)
    {
        return _manager.resume_task(uid);
    }

    template<typename Manager, std::size_t ScratchBytes>
    status_code internal_channel<Manager, ScratchBytes>::complete_task(task_uid_t uid, completion_reason reason)
    {
        return _manager.complete_task(uid, reason);
    }

} // namespace etask::core::channels

#endif // ETASK_CORE_CHANNELS_INTERNAL_CHANNEL_TPP_
