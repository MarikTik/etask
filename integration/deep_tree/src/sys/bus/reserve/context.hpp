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
    //! etask:doc class d878e1658c64
    /**
    * @brief Shared state and hardware for the `reserve` scope - three ordinary siblings, low in the uid space
    *
    * `Tree.__assign_uids` hands out uids lowest-first to tasks sorted by
    * dotted path, so these three - alphabetically first in the whole tree -
    * land in the single digits while the mesh takes everything above. That
    * makes them the cheap end of the space to check: the width is two bytes
    * for all 294, so these are the tasks that would still be readable if
    * something silently narrowed a uid to the value it happens to hold.
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
