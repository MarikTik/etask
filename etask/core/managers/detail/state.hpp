// SPDX-License-Identifier: MIT
/**
* @file state.hpp
*
* @brief Where a live suspendable task sits on the running/suspended axis.
*
* @ingroup etask_core etask::core::managers
*
* @note Internal. Only @ref stateful_task_manager needs this: it is the shape of
*       that manager's per-record bookkeeping, not something a task or an
*       application ever names. Nothing outside `etask::core::managers` should
*       reach for it.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-25
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_MANAGERS_DETAIL_STATE_HPP_
#define ETASK_CORE_MANAGERS_DETAIL_STATE_HPP_
#include <cstdint>

namespace etask::core::managers::detail {

    /**
    * @enum state
    *
    * @brief Where a live stateful task sits on the running/suspended axis.
    *
    * Four states, one byte, mutually exclusive - which is the point. The two
    * transitions that run a hook (`pausing` and `resuming`) fire it *on the
    * transition* and then move off, so a hook cannot fire twice or go unfired.
    * A pause and a resume requested within the same tick simply supersede one
    * another: neither hook runs, because neither transition was ever taken.
    *
    * Concluding is deliberately **not** represented here. That is carried by the
    * record's `completion_reason`, which already distinguishes running, aborted,
    * and force-completed. Two representations of "is this task ending" could
    * disagree with each other; one cannot.
    */
    enum class state : std::uint8_t {
        running,  /**< Executing: `on_execute()` runs each tick. */
        pausing,  /**< Pause requested; `on_pause()` runs on the next tick, then -> `paused`. */
        paused,   /**< Suspended: no `on_execute()`. A resume moves it to `resuming`. */
        resuming  /**< Resume requested; `on_resume()` runs on the next tick, then -> `running`. */
    };

} // namespace etask::core::managers::detail

#endif // ETASK_CORE_MANAGERS_DETAIL_STATE_HPP_
