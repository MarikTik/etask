//! etask:doc file a4594b51200f
/**
* @file context.hpp
*
* @brief Local context for the `arms` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_ARMS_CONTEXT_HPP_
#define SYS_ARMS_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
#include "left/context.hpp"  //! etask:item left
#include "right/context.hpp"  //! etask:item right
//! etask:end child_includes

namespace sys::arms {
    //! etask:doc class ad72221b3b4c
    /**
    * @brief Shared state and hardware for the `arms` scope - the two arms
    *
    * Injected by reference into every task in `sys::arms`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        left::context left;  //! etask:item left
        right::context right;  //! etask:item right
        //! etask:end children
    };
} // namespace sys::arms
#endif // SYS_ARMS_CONTEXT_HPP_
