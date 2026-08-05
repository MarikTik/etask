//! etask:doc file 8aa76c3171bc
/**
* @file context.hpp
*
* @brief Local context for the `right` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_ARMS_RIGHT_CONTEXT_HPP_
#define SYS_ARMS_RIGHT_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::arms::right {
    //! etask:doc class 0add14023c4c
    /**
    * @brief Shared state and hardware for the `right` scope - an articulated arm with a gripper
    *
    * Injected by reference into every task in `sys::arms::right`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::arms::right
#endif // SYS_ARMS_RIGHT_CONTEXT_HPP_
