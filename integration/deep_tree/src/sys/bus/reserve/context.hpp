//! etask:doc file 19f5a374f2f5
/**
* @file context.hpp
*
* @brief Local context for the `reserve` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_BUS_RESERVE_CONTEXT_HPP_
#define SYS_BUS_RESERVE_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::bus::reserve {
    //! etask:doc class e84e1b2332d5
    /**
    * @brief Shared state and hardware for the `reserve` scope - tasks holding pinned, explicit uids
    *
    * Explicit uids are a wire commitment made in the schema rather than
    * derived from a path, so they are the one thing the ledger must honor
    * over its own record. The three below sit at the low, middle, and top
    * of the two-byte space.
    *
    * Injected by reference into every task in `sys::bus::reserve`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::bus::reserve
#endif // SYS_BUS_RESERVE_CONTEXT_HPP_
