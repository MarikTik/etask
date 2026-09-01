//! etask:doc file c4e7ad3eda53
/**
* @file context.hpp
*
* @brief Local context for the `stateful` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_STATEFUL_CONTEXT_HPP_
#define SYS_STATEFUL_CONTEXT_HPP_
#include "support/lifecycle/recorder.hpp"
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::stateful {
    //! etask:doc class c6a1016a8394
    /**
    * @brief Shared state and hardware for the `stateful` scope - the suspendable tier
    *
    * The only tier the manager accepts pause and resume for. Its tasks hold
    * something that must be handled before suspension - here, a recorder that
    * must show the pause bracket closed in the right order.
    *
    * Injected by reference into every task in `sys::stateful`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        /**
        * @brief The ledger `resumable` records its suspension bracket in.
        *
        * This is the tier whose evidence matters most: `on_pause()` and
        * `on_resume()` are pure virtuals the task is *required* to implement,
        * which means the compiler proves they exist but nothing proves the
        * manager ever calls them. The pause and resume counts here are that
        * proof.
        */
        support::lifecycle::recorder recorder{};

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::stateful
#endif // SYS_STATEFUL_CONTEXT_HPP_
