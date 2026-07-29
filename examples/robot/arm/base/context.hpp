// SPDX-License-Identifier: MIT
/**
* @file context.hpp
*
* @brief Local context for the `base` scope (hardware handles, state).
*
* @note Generated once by etask, then owned by you. Add whatever hardware
*       handles and state the tasks in this scope need to operate on.
*/
#ifndef TASKS_ARM_BASE_CONTEXT_HPP_
#define TASKS_ARM_BASE_CONTEXT_HPP_

namespace tasks::arm::base {
    /**
    * @brief Shared state and hardware for the `base` scope - a revolute joint, one definition reused per physical joint
    *
    * Injected by reference into every task in `tasks::arm::base`;
    * a task reads and mutates it to coordinate with its siblings in the scope.
    */
    class context {
    public:
        // TODO: add hardware handles / state for this scope.
    };
} // namespace tasks::arm::base
#endif // TASKS_ARM_BASE_CONTEXT_HPP_
