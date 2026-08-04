// SPDX-License-Identifier: MIT
/**
* @file context.hpp
*
* @brief Local context for the `arms` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
#ifndef SYSTEM_ARMS_CONTEXT_HPP_
#define SYSTEM_ARMS_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
#include "left/context.hpp"  //! etask:item left
#include "right/context.hpp"  //! etask:item right
//! etask:end child_includes

namespace system::arms {
    /**
    * @brief Shared state and hardware for the `arms` scope - the two arms
    *
    * Injected by reference into every task in `system::arms`,
    * which may also reach into the child-scope contexts it holds.
    */
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        left::context left;  //! etask:item left
        right::context right;  //! etask:item right
        //! etask:end children
    };
} // namespace system::arms
#endif // SYSTEM_ARMS_CONTEXT_HPP_
