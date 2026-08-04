// SPDX-License-Identifier: MIT
/**
* @file context.hpp
*
* @brief Local context for the `imu` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
#ifndef SYS_SENSORS_IMU_CONTEXT_HPP_
#define SYS_SENSORS_IMU_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::sensors::imu {
    /**
    * @brief Shared state and hardware for the `imu` scope - inertial measurement unit
    *
    * Injected by reference into every task in `sys::sensors::imu`,
    * which may also reach into the child-scope contexts it holds.
    */
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::sensors::imu
#endif // SYS_SENSORS_IMU_CONTEXT_HPP_
