//! etask:doc file 14476bb75f77
/**
* @file context.hpp
*
* @brief Local context for the `keyed` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_KEYED_CONTEXT_HPP_
#define SYS_KEYED_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::keyed {
    //! etask:doc class b2fdbae73dad
    /**
    * @brief Shared state and hardware for the `keyed` scope - status-keyed returns whose branches differ in width
    *
    * The point of a status-keyed return is that the branches are *not* the same
    * shape - otherwise the status byte would carry no information the values do
    * not. Each task here is steered by a parameter so a test can reach every
    * branch on demand, which is what makes the narrow branches testable at all.
    *
    * Injected by reference into every task in `sys::keyed`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::keyed
#endif // SYS_KEYED_CONTEXT_HPP_
