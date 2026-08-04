// SPDX-License-Identifier: MIT
/**
* @file context.hpp
*
* @brief Local context for the `sensors` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
#ifndef SYS_SENSORS_CONTEXT_HPP_
#define SYS_SENSORS_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
#include "imu/context.hpp"  //! etask:item imu
#include "baro/context.hpp"  //! etask:item baro
#include "gps/context.hpp"  //! etask:item gps
//! etask:end child_includes

namespace sys::sensors {
    /**
    * @brief Shared state and hardware for the `sensors` scope - the flight sensor suite
    *
    * Injected by reference into every task in `sys::sensors`,
    * which may also reach into the child-scope contexts it holds.
    */
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        imu::context imu;  //! etask:item imu
        baro::context baro;  //! etask:item baro
        gps::context gps;  //! etask:item gps
        //! etask:end children
    };
} // namespace sys::sensors
#endif // SYS_SENSORS_CONTEXT_HPP_
