//! etask:doc file 4cdf376d8225
/**
* @file context.hpp
*
* @brief Local context for the `led` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_LED_CONTEXT_HPP_
#define SYS_LED_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::led {
    //! etask:doc class 93753ef124b8
    /**
    * @brief Shared state and hardware for the `led` scope - the on-board status LED
    *
    * Injected by reference into every task in `sys::led`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::led
#endif // SYS_LED_CONTEXT_HPP_
