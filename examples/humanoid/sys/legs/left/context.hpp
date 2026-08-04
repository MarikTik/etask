// SPDX-License-Identifier: MIT
/**
* @file context.hpp
*
* @brief Local context for the `left` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
#ifndef SYS_LEGS_LEFT_CONTEXT_HPP_
#define SYS_LEGS_LEFT_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::legs::left {
    /**
    * @brief Shared state and hardware for the `left` scope - a leg
    *
    * Injected by reference into every task in `sys::legs::left`,
    * which may also reach into the child-scope contexts it holds.
    */
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::legs::left
#endif // SYS_LEGS_LEFT_CONTEXT_HPP_
