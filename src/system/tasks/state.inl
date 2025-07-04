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
#ifndef SYSTEM_TASKS_STATE_INL_
#define SYSTEM_TASKS_STATE_INL_
#include "state.hpp"

namespace etask::system::tasks {
    inline bool state::is_started() const {
        return _state & started;
    }
    
    inline bool state::is_finished() const {
        return _state & finished;
    }
    
    inline bool state::is_paused() const {
        return _state & paused;
    }
    
    inline bool state::is_resumed() const
    {
        return _state & resumed;
    }
    
    inline state& state::set_paused() {
        _state = static_cast<state_flags>((_state | paused) & ~resumed);
        return *this;
    }
    
    inline state &state::set_resumed()
    {
        _state = static_cast<state_flags>((_state | resumed) & ~paused);
        return *this;
    }
    
    inline state& state::set_started() {
        _state = static_cast<state_flags>(_state | started);
        return *this;
    }
    
    inline state& state::set_finished() {
        _state = static_cast<state_flags>(_state | finished);
        return *this;
    }
} // namespace etask::system::tasks

#endif // SYSTEM_TASKS_STATE_INL_
