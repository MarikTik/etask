//! etask:doc file e83c8d1e23b7
/**
* @file context.hpp
*
* @brief Local context for the `bus` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_BUS_CONTEXT_HPP_
#define SYS_BUS_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
#include "link_state/context.hpp"  //! etask:item link_state
#include "link/context.hpp"  //! etask:item link
#include "reserve/context.hpp"  //! etask:item reserve
//! etask:end child_includes

namespace sys::bus {
    //! etask:doc class 8dee7385b3cb
    /**
    * @brief Shared state and hardware for the `bus` scope - the concrete side of the tree
    *
    * No abstract scopes below this point. Tasks here pin explicit uids among
    * derived siblings, and the two `link*` scopes are the flattened-name near
    * miss described at the top of this file.
    *
    * Injected by reference into every task in `sys::bus`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        link_state::context link_state;  //! etask:item link_state
        link::context link;  //! etask:item link
        reserve::context reserve;  //! etask:item reserve
        //! etask:end children
    };
} // namespace sys::bus
#endif // SYS_BUS_CONTEXT_HPP_
