//! etask:doc file 6a85a8b5d0cd
/**
* @file context.hpp
*
* @brief Local context for the `bulk` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_BULK_CONTEXT_HPP_
#define SYS_BULK_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::bulk {
    //! etask:doc class 8f529c567d00
    /**
    * @brief Shared state and hardware for the `bulk` scope - the wide subsystem, carried by `net` alone
    *
    * Exists to make one link's frames genuinely larger than the other's. Its task takes the widest parameter list here and returns the widest result, so `net` - the only link carrying it - must size both directions for it while `bench` must not.
    *
    * Injected by reference into every task in `sys::bulk`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::bulk
#endif // SYS_BULK_CONTEXT_HPP_
