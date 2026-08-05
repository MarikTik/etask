//! etask:doc file 413ed4adea10
/**
* @file context.hpp
*
* @brief Local context for the `nav` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_NAV_CONTEXT_HPP_
#define SYS_NAV_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::nav {
    //! etask:doc class 22c443dd4504
    /**
    * @brief Shared state and hardware for the `nav` scope - the navigation layer
    *
    * Turns high-level intent into rotor commands. Holds no hardware of its own;
    * its context reaches into the rotor and sensor subsystems it coordinates.
    *
    * Injected by reference into every task in `sys::nav`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::nav
#endif // SYS_NAV_CONTEXT_HPP_
