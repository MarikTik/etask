//! etask:doc file 6f16e817af8f
/**
* @file context.hpp
*
* @brief Local context for the `polled` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_POLLED_CONTEXT_HPP_
#define SYS_POLLED_CONTEXT_HPP_
#include "support/lifecycle/recorder.hpp"
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::polled {
    //! etask:doc class b04ec02a1652
    /**
    * @brief Shared state and hardware for the `polled` scope - the runs-across-ticks tier
    *
    * Tasks the manager drives until they say they are done. Nothing here can
    * be suspended: that is the distinction from the stateful scope below, and
    * `not_pausable` exists to prove the manager enforces it.
    *
    * Injected by reference into every task in `sys::polled`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        /**
        * @brief `count_to`'s ledger.
        *
        * One recorder per task rather than one for the scope, because this tier
        * is the only one holding two tasks and a scenario runs them together.
        * Sharing would merge two traces into one and make "never_ends executed
        * twice" indistinguishable from "each executed once".
        */
        support::lifecycle::recorder count_to_recorder{};

        /// @brief `never_ends`'s ledger. Kept apart from `count_to`'s; see above.
        support::lifecycle::recorder never_ends_recorder{};

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::polled
#endif // SYS_POLLED_CONTEXT_HPP_
