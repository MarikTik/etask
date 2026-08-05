//! etask:doc file c751f9881da4
/**
* @file context.hpp
*
* @brief Local context for the `baro` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_SENSORS_BARO_CONTEXT_HPP_
#define SYS_SENSORS_BARO_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::sensors::baro {
    //! etask:doc class cabb796616d9
    /**
    * @brief Shared state and hardware for the `baro` scope - barometric altimeter
    *
    * Injected by reference into every task in `sys::sensors::baro`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::sensors::baro
#endif // SYS_SENSORS_BARO_CONTEXT_HPP_
