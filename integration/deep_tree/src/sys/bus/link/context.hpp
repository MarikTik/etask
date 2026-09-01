//! etask:doc file 2acd5035c67d
/**
* @file context.hpp
*
* @brief Local context for the `link` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_BUS_LINK_CONTEXT_HPP_
#define SYS_BUS_LINK_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::bus::link {
    //! etask:doc class cd1e42b503e3
    /**
    * @brief Shared state and hardware for the `link` scope - link, as a scope whose child carries the underscore instead
    *
    * Injected by reference into every task in `sys::bus::link`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::bus::link
#endif // SYS_BUS_LINK_CONTEXT_HPP_
