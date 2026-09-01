//! etask:doc file 367e56e4bf1d
/**
* @file context.hpp
*
* @brief Local context for the `mixed` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_MIXED_CONTEXT_HPP_
#define SYS_MIXED_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::mixed {
    //! etask:doc class 6b7d2a2110e2
    /**
    * @brief Shared state and hardware for the `mixed` scope - narrow and wide types interleaved, in padding-hostile orders
    *
    * A flat codec has no padding; a struct laid out the same way does. Every
    * task here is an ordering whose equivalent C struct would carry interior
    * padding on at least one of the two targets, so a serializer that ever
    * took the address of a struct - or that rounded a field's offset up to its
    * own alignment - disagrees with one that appends bytes.
    *
    * The read on a failure is positional: the first field that differs names
    * the boundary the padding was inserted at.
    *
    * Injected by reference into every task in `sys::mixed`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::mixed
#endif // SYS_MIXED_CONTEXT_HPP_
