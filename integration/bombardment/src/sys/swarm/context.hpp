//! etask:doc file 4f511ff68cc3
/**
* @file context.hpp
*
* @brief Local context for the `swarm` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_SWARM_CONTEXT_HPP_
#define SYS_SWARM_CONTEXT_HPP_
#include <cstdint>
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::swarm {
    //! etask:doc class 90cd96ebefac
    /**
    * @brief Shared state and hardware for the `swarm` scope - the bombardment surface - tasks that exist only to occupy records
    *
    * Four uids with deliberately different concurrency, so the driver can pick
    * which limit it runs into. `salvo` and `probe` together fill the tier;
    * `volley` is the narrow one saturated while the tier still has room; and
    * `single` is the degenerate case of a uid that admits exactly one instance.
    *
    * Injected by reference into every task in `sys::swarm`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        /**
        * @brief How many polled tasks in this scope have been constructed.
        *
        * Counted in the scope rather than in each task because a task's own
        * fields die with it, and the interesting question here is about the
        * ones that are *gone*: a record the manager failed to reclaim shows up
        * as a construction with no matching conclusion. Comparing this against
        * @ref concluded is what turns "the manager still accepts work" into
        * "the manager still accepts work and did not quietly retain anything".
        */
        std::uint32_t constructed = 0;

        /**
        * @brief How many of those tasks have run their `on_complete`.
        *
        * Incremented on every conclusion path - natural, aborted, or
        * force-completed - so a lagging count means a task was dropped without
        * being concluded, not merely that it ended in an unusual way.
        */
        std::uint32_t concluded = 0;

        /**
        * @brief The largest number of this scope's tasks alive at any one moment.
        *
        * The observed peak, as distinct from the budget that permits it. The
        * harness asserts the peak actually reached the budget: a check that
        * "registration failed at the seventh" proves nothing if the first six
        * never really occupied a record.
        */
        std::uint32_t peak_live = 0;

        /**
        * @brief Records the birth of a task and updates the peak.
        *
        * Bundled into one call rather than left to each task's constructor so
        * that the peak cannot drift from the counts it is derived from - there
        * is one place where a task becomes live.
        */
        void note_constructed() noexcept
        {
            ++constructed;
            const std::uint32_t live = constructed - concluded;
            if (live > peak_live) peak_live = live;
        }

        /// @brief Records that a task concluded, on whichever path it took.
        void note_concluded() noexcept { ++concluded; }

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::swarm
#endif // SYS_SWARM_CONTEXT_HPP_
