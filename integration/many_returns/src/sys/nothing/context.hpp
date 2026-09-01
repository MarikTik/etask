//! etask:doc file b95f6d0f73b7
/**
* @file context.hpp
*
* @brief Local context for the `nothing` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_NOTHING_CONTEXT_HPP_
#define SYS_NOTHING_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::nothing {
    //! etask:doc class 49cece0bea68
    /**
    * @brief Shared state and hardware for the `nothing` scope - tasks that answer with a status and no bytes
    *
    * A task with no `returns:` still replies - the reply is [uid][status] with
    * an empty result region. It is worth its own scope because the empty case is
    * where an off-by-one in the result offset does the least visible damage: the
    * peer reads zero bytes either way and only the status is wrong.
    *
    * Injected by reference into every task in `sys::nothing`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::nothing
#endif // SYS_NOTHING_CONTEXT_HPP_
