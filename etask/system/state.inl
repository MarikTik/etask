// SPDX-License-Identifier: BSL-1.1
/**
* @file state.inl
*
* @brief implementation of state.inl methods.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-03
*
* @copyright Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_SYSTEM_STATE_INL_
#define ETASK_SYSTEM_STATE_INL_
#include "state.hpp"

namespace etask::system {

    inline bool state::is_started() const noexcept {
        return _state & started;
    }

    inline bool state::is_finished() const noexcept {
        return _state & finished;
    }

    inline bool state::is_paused() const noexcept {
        return _state & paused;
    }

    inline bool state::is_resumed() const noexcept {
        return _state & resumed;
    }

    inline bool state::is_aborted() const noexcept {
        return _state & aborted;
    }

    inline bool state::is_running() const noexcept
    {
        return _state & running;
    }

    inline bool state::is_idle() const noexcept
    {
        return _state & idle;
    }

    inline state& state::set_paused() noexcept {
        _state = static_cast<state_flags>((_state | paused) & ~resumed);
        return *this;
    }

    inline state &state::set_resumed() noexcept
    {
        _state = static_cast<state_flags>((_state | resumed) & ~paused);
        return *this;
    }

    inline state& state::set_started() noexcept {
        _state = static_cast<state_flags>(_state | started);
        return *this;
    }

    inline state& state::set_finished() noexcept {
        _state = static_cast<state_flags>(_state | finished);
        return *this;
    }

    inline state &state::set_aborted() noexcept {
        _state = static_cast<state_flags>(_state | aborted);
        return *this;
    }

    inline state &state::set_running() noexcept
    {
        _state = static_cast<state_flags>((_state | running) & ~idle);
        return *this;
    }

    inline state &state::set_idle() noexcept
    {
        _state = static_cast<state_flags>((_state | idle) & ~running);
        return *this;
    }
} // namespace etask::system

#endif // ETASK_SYSTEM_STATE_INL_
