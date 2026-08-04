// SPDX-License-Identifier: MIT
/**
* @file context.hpp
*
* @brief Local context for the `rl` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
#ifndef SYSTEM_ROTORS_RL_CONTEXT_HPP_
#define SYSTEM_ROTORS_RL_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace system::rotors::rl {
    /**
    * @brief Shared state and hardware for the `rl` scope.
    *
    * Injected by reference into every task in `system::rotors::rl`,
    * which may also reach into the child-scope contexts it holds.
    */
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace system::rotors::rl
#endif // SYSTEM_ROTORS_RL_CONTEXT_HPP_
