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

    template<typename Manager>
    internal_channel<Manager>::internal_channel(Manager& manager) noexcept
        : _manager{manager}
    {
    }

    template<typename Manager>
    void internal_channel<Manager>::complete(
        [[maybe_unused]] std::uint8_t initiator_id,
        [[maybe_unused]] task_uid_t uid,
        [[maybe_unused]] status_code code,
        completion_reason reason,
        task<task_uid_t>& t)
    {
        // A bound region with no room: the completion is real, so a task that
        // returns values is not misusing `outcome` and must not trip its assert,
        // but there is nowhere for the bytes to go and nothing would ever read
        // them. This channel used to hold a std::array to pack into and then
        // ignore, which meant carrying a buffer sized by guesswork - the default
        // was 64 bytes - and silently truncating any task that returned more.
        // Discarding needs no storage.
        const detail::result_region discard = detail::discard_region();
        detail::result_region_scope region{discard.data, discard.capacity};
        // Deliberately dropped: an internal task's result goes nowhere yet (a
        // future track_task will capture it). The task still runs, and still
        // reaches on_complete exactly as a wire task does.
        [[maybe_unused]] const outcome discarded = t.on_complete(reason);
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

} // namespace etask::core::channels

#endif // ETASK_CORE_CHANNELS_INTERNAL_CHANNEL_TPP_
