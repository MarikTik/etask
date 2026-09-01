//! etask:doc file 48dae6983967
/**
* @file context.hpp
*
* @brief Local context for the `telemetry` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_TELEMETRY_CONTEXT_HPP_
#define SYS_TELEMETRY_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::telemetry {
    //! etask:doc class af246412a26f
    /**
    * @brief Shared state and hardware for the `telemetry` scope - the narrow subsystem, carried by `bench` alone
    *
    * The mirror of `bulk`: narrow, and carried by the other link. Having a link-exclusive subsystem on *each* side is what lets verify.py assert refusal in both directions, which a single exclusive subsystem could not.
    *
    * Injected by reference into every task in `sys::telemetry`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::telemetry
#endif // SYS_TELEMETRY_CONTEXT_HPP_
