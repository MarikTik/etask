//! etask:doc file aa76e680fc6b
/**
* @file context.hpp
*
* @brief Local context for the `instant` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_INSTANT_CONTEXT_HPP_
#define SYS_INSTANT_CONTEXT_HPP_
#include "support/lifecycle/recorder.hpp"
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::instant {
    //! etask:doc class 1e95bb026e04
    /**
    * @brief Shared state and hardware for the `instant` scope - the fire-and-forget tier
    *
    * Commands that run to completion inside the call that delivers them. They
    * never register, never tick, and never reply - so the only evidence they
    * ran is what they leave in this scope's context.
    *
    * Injected by reference into every task in `sys::instant`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        /**
        * @brief The ledger this tier's commands record their arrival in.
        *
        * An instant command sends no reply, so this is the *only* channel by
        * which it can be observed at all - which is exactly the property the
        * fire-and-forget tier is here to demonstrate.
        */
        support::lifecycle::recorder recorder{};

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::instant
#endif // SYS_INSTANT_CONTEXT_HPP_
