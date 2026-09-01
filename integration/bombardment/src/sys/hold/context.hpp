//! etask:doc file 8818feb4a06c
/**
* @file context.hpp
*
* @brief Local context for the `hold` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_HOLD_CONTEXT_HPP_
#define SYS_HOLD_CONTEXT_HPP_
#include <cstdint>
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::hold {
    //! etask:doc class 4a3f3a466d22
    /**
    * @brief Shared state and hardware for the `hold` scope - the stateful tier - a separate manager with a separate budget
    *
    * Kept apart from `swarm` because it is a different manager: filling the
    * polled tier must leave this one untouched, and the driver asserts exactly
    * that. A suspended task still holds its record, so this tier can be filled
    * with tasks that are not even running.
    *
    * Injected by reference into every task in `sys::hold`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        /// @brief How many stateful tasks in this scope have been constructed.
        std::uint32_t constructed = 0;

        /// @brief How many of those have run their `on_complete`.
        std::uint32_t concluded = 0;

        /**
        * @brief The largest number of this scope's tasks alive at any one moment.
        *
        * Separate from the polled tier's peak on purpose. The two tiers are two
        * managers with two independent budgets, and the claim the harness has to
        * substantiate is that exhausting one leaves the other's capacity intact -
        * which requires being able to see each tier's occupancy on its own.
        */
        std::uint32_t peak_live = 0;

        /**
        * @brief How many `on_pause` calls this scope's tasks have seen.
        *
        * A paused stateful task keeps its record, so pausing is the cheapest way
        * to hold this tier full without spending ticks. Counting the callback
        * proves the suspension actually happened rather than the pause request
        * merely being accepted.
        */
        std::uint32_t paused = 0;

        /// @brief How many `on_resume` calls this scope's tasks have seen.
        std::uint32_t resumed = 0;

        /// @brief Records the birth of a task and updates the peak. See `swarm::context`.
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
} // namespace sys::hold
#endif // SYS_HOLD_CONTEXT_HPP_
