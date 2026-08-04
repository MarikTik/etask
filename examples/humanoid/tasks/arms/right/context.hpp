// SPDX-License-Identifier: MIT
/**
* @file context.hpp
*
* @brief Local context for the `right` scope (hardware handles, state).
*
* @note Generated once by etask, then owned by you. Add whatever hardware
*       handles and state the tasks in this scope need to operate on.
*/
#ifndef TASKS_ARMS_RIGHT_CONTEXT_HPP_
#define TASKS_ARMS_RIGHT_CONTEXT_HPP_

namespace tasks::arms::right {
    /**
    * @brief Shared state and hardware for the `right` scope - an articulated arm with a gripper
    *
    * Injected by reference into every task in `tasks::arms::right`;
    * a task reads and mutates it to coordinate with its siblings in the scope.
    */
    class context {
    public:
        // TODO: add hardware handles / state for this scope.
    };
} // namespace tasks::arms::right
#endif // TASKS_ARMS_RIGHT_CONTEXT_HPP_
