// SPDX-License-Identifier: MIT
/**
* @file context.hpp
*
* @brief Local context for the `legs` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
#ifndef SYS_LEGS_CONTEXT_HPP_
#define SYS_LEGS_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
#include "left/context.hpp"  //! etask:item left
#include "right/context.hpp"  //! etask:item right
//! etask:end child_includes

namespace sys::legs {
    /**
    * @brief Shared state and hardware for the `legs` scope - the two legs
    *
    * Injected by reference into every task in `sys::legs`,
    * which may also reach into the child-scope contexts it holds.
    */
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        left::context left;  //! etask:item left
        right::context right;  //! etask:item right
        //! etask:end children
    };
} // namespace sys::legs
#endif // SYS_LEGS_CONTEXT_HPP_
