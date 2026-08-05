//! etask:doc file cabb1a88a110
/**
* @file context.hpp
*
* @brief The system's composition root - owns every subsystem's context.
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_CONTEXT_HPP_
#define SYS_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
#include "rotors/context.hpp"  //! etask:item rotors
#include "sensors/context.hpp"  //! etask:item sensors
#include "nav/context.hpp"  //! etask:item nav
//! etask:end child_includes

namespace sys {
    //! etask:doc class 444dbac04d73
    /**
    * @brief The system composition root: every subsystem's context, owned here.
    *
    * Constructed once, top-down; a system-level task (e.g. reboot) receives this
    * and can reach any subsystem through it.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        rotors::context rotors;  //! etask:item rotors
        sensors::context sensors;  //! etask:item sensors
        nav::context nav;  //! etask:item nav
        //! etask:end children
    };
} // namespace sys
#endif // SYS_CONTEXT_HPP_
