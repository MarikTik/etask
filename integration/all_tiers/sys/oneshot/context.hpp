//! etask:doc file 0a32450fd42b
/**
* @file context.hpp
*
* @brief Local context for the `oneshot` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_ONESHOT_CONTEXT_HPP_
#define SYS_ONESHOT_CONTEXT_HPP_
#include "support/lifecycle/recorder.hpp"
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::oneshot {
    //! etask:doc class f9c3899f745e
    /**
    * @brief Shared state and hardware for the `oneshot` scope - the run-once-and-answer tier
    *
    * Injected by reference into every task in `sys::oneshot`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        /**
        * @brief The ledger this tier's task records its lifecycle in.
        *
        * A oneshot answers, so its trace also reaches the host in its `outcome`.
        * Keeping it here as well is what lets `verify.py` cross-check the two:
        * a trace that survived the reply but not the context, or the reverse,
        * would mean the task and its result had come apart.
        */
        support::lifecycle::recorder recorder{};

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::oneshot
#endif // SYS_ONESHOT_CONTEXT_HPP_
