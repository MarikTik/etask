//! etask:doc file 4f511ff68cc3
/**
* @file context.hpp
*
* @brief Local context for the `swarm` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_SWARM_CONTEXT_HPP_
#define SYS_SWARM_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::swarm {
    //! etask:doc class 90cd96ebefac
    /**
    * @brief Shared state and hardware for the `swarm` scope - the bombardment surface - tasks that exist only to occupy records
    *
    * Four uids with deliberately different concurrency, so the driver can pick
    * which limit it runs into. `salvo` and `probe` together fill the tier;
    * `volley` is the narrow one saturated while the tier still has room; and
    * `single` is the degenerate case of a uid that admits exactly one instance.
    *
    * Injected by reference into every task in `sys::swarm`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::swarm
#endif // SYS_SWARM_CONTEXT_HPP_
