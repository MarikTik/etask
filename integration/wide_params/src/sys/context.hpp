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
#include "echo/context.hpp"  //! etask:item echo
#include "mixed/context.hpp"  //! etask:item mixed
#include "wide/context.hpp"  //! etask:item wide
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
        echo::context echo;  //! etask:item echo
        mixed::context mixed;  //! etask:item mixed
        wide::context wide;  //! etask:item wide
        //! etask:end children
    };
} // namespace sys
#endif // SYS_CONTEXT_HPP_
