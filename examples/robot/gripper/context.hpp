// SPDX-License-Identifier: MIT
/**
* @file context.hpp
*
* @brief Local context for the `gripper` scope (hardware handles, state).
*
* @note Generated once by etask, then owned by you. Add whatever hardware
*       handles and state the tasks in this scope need to operate on.
*/
#ifndef TASKS_GRIPPER_CONTEXT_HPP_
#define TASKS_GRIPPER_CONTEXT_HPP_

namespace tasks::gripper {
    /**
    * @brief Shared state and hardware for the `gripper` scope - two-finger gripper
    *
    * The end-effector: two opposing fingers on a single actuator, plus a force
    * sensor used for grasp detection.
    *
    * Injected by reference into every task in `tasks::gripper`;
    * a task reads and mutates it to coordinate with its siblings in the scope.
    */
    class context {
    public:
        // TODO: add hardware handles / state for this scope.
    };
} // namespace tasks::gripper
#endif // TASKS_GRIPPER_CONTEXT_HPP_
