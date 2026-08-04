// SPDX-License-Identifier: MIT
/**
* @file context.hpp
*
* @brief Local context for the `imu` scope (hardware handles, state).
*
* @note Generated once by etask, then owned by you. Add whatever hardware
*       handles and state the tasks in this scope need to operate on.
*/
#ifndef TASKS_HEAD_IMU_CONTEXT_HPP_
#define TASKS_HEAD_IMU_CONTEXT_HPP_

namespace tasks::head::imu {
    /**
    * @brief Shared state and hardware for the `imu` scope - inertial measurement unit
    *
    * Injected by reference into every task in `tasks::head::imu`;
    * a task reads and mutates it to coordinate with its siblings in the scope.
    */
    class context {
    public:
        // TODO: add hardware handles / state for this scope.
    };
} // namespace tasks::head::imu
#endif // TASKS_HEAD_IMU_CONTEXT_HPP_
