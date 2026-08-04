// SPDX-License-Identifier: MIT
/**
* @file context.hpp
*
* @brief Local context for the `head` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
#ifndef SYSTEM_HEAD_CONTEXT_HPP_
#define SYSTEM_HEAD_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
#include "imu/context.hpp"  //! etask:item imu
//! etask:end child_includes

namespace system::head {
    /**
    * @brief Shared state and hardware for the `head` scope - sensor head
    *
    * Injected by reference into every task in `system::head`,
    * which may also reach into the child-scope contexts it holds.
    */
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        imu::context imu;  //! etask:item imu
        //! etask:end children
    };
} // namespace system::head
#endif // SYSTEM_HEAD_CONTEXT_HPP_
