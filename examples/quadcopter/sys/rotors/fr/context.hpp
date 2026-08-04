// SPDX-License-Identifier: MIT
/**
* @file context.hpp
*
* @brief Local context for the `fr` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
#ifndef SYS_ROTORS_FR_CONTEXT_HPP_
#define SYS_ROTORS_FR_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::rotors::fr {
    /**
    * @brief Shared state and hardware for the `fr` scope.
    *
    * Injected by reference into every task in `sys::rotors::fr`,
    * which may also reach into the child-scope contexts it holds.
    */
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::rotors::fr
#endif // SYS_ROTORS_FR_CONTEXT_HPP_
