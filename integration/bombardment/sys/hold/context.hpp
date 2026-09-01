//! etask:doc file 8818feb4a06c
/**
* @file context.hpp
*
* @brief Local context for the `hold` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_HOLD_CONTEXT_HPP_
#define SYS_HOLD_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::hold {
    //! etask:doc class 4a3f3a466d22
    /**
    * @brief Shared state and hardware for the `hold` scope - the stateful tier - a separate manager with a separate budget
    *
    * Kept apart from `swarm` because it is a different manager: filling the
    * polled tier must leave this one untouched, and the driver asserts exactly
    * that. A suspended task still holds its record, so this tier can be filled
    * with tasks that are not even running.
    *
    * Injected by reference into every task in `sys::hold`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::hold
#endif // SYS_HOLD_CONTEXT_HPP_
