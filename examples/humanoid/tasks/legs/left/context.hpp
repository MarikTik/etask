// SPDX-License-Identifier: MIT
/**
* @file context.hpp
*
* @brief Local context for the `left` scope (hardware handles, state).
*
* @note Generated once by etask, then owned by you. Add whatever hardware
*       handles and state the tasks in this scope need to operate on.
*/
#ifndef TASKS_LEGS_LEFT_CONTEXT_HPP_
#define TASKS_LEGS_LEFT_CONTEXT_HPP_

namespace tasks::legs::left {
    /**
    * @brief Shared state and hardware for the `left` scope - a leg
    *
    * Injected by reference into every task in `tasks::legs::left`;
    * a task reads and mutates it to coordinate with its siblings in the scope.
    */
    class context {
    public:
        // TODO: add hardware handles / state for this scope.
    };
} // namespace tasks::legs::left
#endif // TASKS_LEGS_LEFT_CONTEXT_HPP_
