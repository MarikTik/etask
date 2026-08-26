// SPDX-License-Identifier: MIT
/**
* @file task_manager.hpp
*
* @brief Declares `task_manager`, the one manager an application talks to.
*
* @ingroup etask_core etask::core::managers
*
* A project's tasks are split across three tiers with genuinely different
* machinery behind them (see @ref tasks.hpp). `task_manager` is the single front
* door: it holds one of each sub-manager and routes every call to whichever one
* owns the uid in question.
*
* ## Routing is free
*
* Which manager owns a uid is a property of the schema, known at compile time.
* Each sub-manager answers `owns(raw_uid)` as a constant expression, so the
* routing in every entry point folds down to the same work a single manager
* would have done - a uid lookup - with no extra runtime branch on tier.
*
* ## Unused tiers cost nothing
*
* A tier with no tasks is not merely empty at runtime; it is **never
* instantiated**. Passing an empty typelist selects a specialization with no
* storage, no code, and no members - so a project of pure fire-and-forget
* commands carries no polling loop, no task vector, and no virtual dispatch
* anywhere, while one with nothing to suspend carries no suspension machinery.
*
* ## Directives against an instant command
*
* Pause, resume, and complete all address a *live* task. An @ref instant_task is
* never live - it runs to completion inside the call that delivered it - so all
* three are answered with `status_code::task_not_addressable`. That is a
* structural fact about the uid, not a race: it is knowable at compile time and
* means the caller asked for something that cannot exist, as distinct from
* `task_not_registered`, which is the ordinary "valid uid, nothing running right
* now" answer for a managed task that already finished.
*
* @code
* using manager_t = etask::core::managers::task_manager_from_t<
*     generated::instant_tasks,
*     generated::polled_tasks,
*     generated::stateful_tasks>;
* @endcode
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-25
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_MANAGERS_TASK_MANAGER_HPP_
#define ETASK_CORE_MANAGERS_TASK_MANAGER_HPP_
#include "instant_task_manager.hpp"
#include "polled_task_manager.hpp"
#include "stateful_task_manager.hpp"
#include "detail/empty_managers.hpp"
#include "../channel.hpp"
#include "../status_code.hpp"
#include "../completion_reason.hpp"
#include <etools/meta/typelist.hpp>
#include <cstdint>

namespace etask::core::managers {

    /**
    * @class task_manager
    *
    * @brief Routes every task operation to the sub-manager that owns its tier.
    *
    * @tparam InstantTasks  Typelist of @ref instant_task commands. May be empty.
    * @tparam PolledTasks   Typelist of @ref polled_task types. May be empty.
    * @tparam StatefulTasks Typelist of @ref stateful_task types. May be empty.
    *
    * At least one list must be non-empty; a manager for no tasks at all is
    * rejected.
    */
    template<typename InstantTasks, typename PolledTasks, typename StatefulTasks>
    class task_manager
        // Held as private bases, not members, so that an absent tier - which is
        // an empty class - costs nothing. Empty base optimization is guaranteed
        // by C++17; `[[no_unique_address]]` on a member would say the same thing
        // but is C++20, and this project is C++17. See @ref detail::tier_storage.
        : private detail::tier_storage<0, detail::manager_for_t<instant_task_manager, InstantTasks>>,
          private detail::tier_storage<1, detail::manager_for_t<polled_task_manager, PolledTasks>>,
          private detail::tier_storage<2, detail::manager_for_t<stateful_task_manager, StatefulTasks>>
    {
        /// @brief The instant dispatcher, or an inert stand-in when there are none.
        using instant_t  = detail::manager_for_t<instant_task_manager, InstantTasks>;
        /// @brief The polled manager, or an inert stand-in when there are none.
        using polled_t   = detail::manager_for_t<polled_task_manager, PolledTasks>;
        /// @brief The stateful manager, or an inert stand-in when there are none.
        using stateful_t = detail::manager_for_t<stateful_task_manager, StatefulTasks>;

        /// @brief The base holding the instant dispatcher.
        using instant_base  = detail::tier_storage<0, instant_t>;
        /// @brief The base holding the polled manager.
        using polled_base   = detail::tier_storage<1, polled_t>;
        /// @brief The base holding the stateful manager.
        using stateful_base = detail::tier_storage<2, stateful_t>;

    public:
        /**
        * @typedef task_uid_t
        * @brief The project's task identifier type.
        *
        * Taken from whichever tiers are populated, and required to agree across
        * all of them - one project has one uid space.
        */
        using task_uid_t = detail::common_uid_t<instant_t, polled_t, stateful_t>;

        /**
        * @typedef channel_t
        * @brief The channel type this manager delivers results through.
        */
        using channel_t = channel<task_uid_t>;

    private:
        /// @brief `task_uid_t` normalized to its raw integral form.
        using raw_uid_t = detail::raw_uid_t<task_uid_t>;

    public:
        /**
        * @brief Constructs the manager and its populated sub-managers.
        *
        * @param max_task_load Expected maximum number of concurrently live managed
        *        tasks, passed to the polled and stateful managers. Instant commands
        *        are unaffected - they occupy no storage. Defaults to each
        *        sub-manager's own reserved capacity.
        */
        explicit task_manager(std::size_t max_task_load = 0);

        /// @brief Deleted copy constructor - the sub-managers own task storage in place.
        task_manager(const task_manager&) = delete;
        /// @brief Deleted copy assignment - see the deleted copy constructor.
        task_manager& operator=(const task_manager&) = delete;
        /// @brief Deleted move constructor - see the deleted copy constructor.
        task_manager(task_manager&&) = delete;
        /// @brief Deleted move assignment - see the deleted copy constructor.
        task_manager& operator=(task_manager&&) = delete;

        /**
        * @brief Starts the task identified by `uid`.
        *
        * Routed by tier. For a managed task this registers it, to be driven on
        * subsequent `update()` calls. For an @ref instant_task there is nothing to
        * register: the command **runs to completion before this call returns**, and
        * `origin` goes unused because no reply is ever sent.
        *
        * @tparam Args Task constructor argument types.
        *
        * @param origin       Channel that will receive a managed task's result.
        *        Unused for an instant command.
        * @param initiator_id Id of the device or component asking. Unused for an
        *        instant command.
        * @param uid          Which task to start.
        * @param args         Forwarded to the task's constructor.
        *
        * @return The owning sub-manager's status; `task_unknown` if no tier claims
        *         this uid.
        */
        template<typename... Args>
        [[nodiscard]] status_code register_task(channel_t *origin, std::uint8_t initiator_id, task_uid_t uid, Args&&... args);

        /**
        * @brief Suspends a running task.
        *
        * @param uid Which task to suspend.
        *
        * @return The stateful manager's status if it owns this uid;
        *         `task_not_pausable` if a polled task owns it - it is live, but has
        *         no suspension to honor; `task_not_addressable` if it is an instant
        *         command, which is never live; `task_unknown` if no tier claims it.
        */
        [[nodiscard]] status_code pause_task(task_uid_t uid);

        /**
        * @brief Resumes a suspended task.
        *
        * @param uid Which task to resume.
        *
        * @return As @ref pause_task, for the mirror operation.
        */
        [[nodiscard]] status_code resume_task(task_uid_t uid);

        /**
        * @brief Forces a live task to conclude before it would on its own.
        *
        * @param uid    Which task to conclude.
        * @param reason Why. Never `completion_reason::finished`.
        *
        * @return The owning sub-manager's status; `task_not_addressable` if it is
        *         an instant command, which has already finished by the time anyone
        *         could ask; `task_unknown` if no tier claims this uid.
        */
        [[nodiscard]] status_code complete_task(task_uid_t uid, completion_reason reason);

        /**
        * @brief Runs one cycle over every live managed task.
        *
        * Drives the polled and stateful managers in turn. Instant commands are not
        * involved - they never survive to see a tick.
        *
        * Call periodically from the application's main loop.
        */
        void update();

    private:
        /// @brief The instant command dispatcher. Stateless; holds nothing.
        [[nodiscard]] instant_t& instant() noexcept;
        /// @brief The manager owning and driving the polled tasks.
        [[nodiscard]] polled_t& polled() noexcept;
        /// @brief The manager owning and driving the stateful tasks.
        [[nodiscard]] stateful_t& stateful() noexcept;

        /**
        * @brief The status for a directive aimed at a uid no live task can hold.
        *
        * Separates the two ways an address can fail to name something live, which
        * call for different reactions from the caller:
        *
        * - an instant command's uid is valid but **never** addressable, because the
        *   command does not persist. The caller asked for something impossible and
        *   should stop asking: `task_not_addressable`.
        * - a uid no tier claims at all is simply not this firmware's:
        *   `task_unknown`.
        *
        * @param raw_uid The uid that failed to route.
        * @return The status explaining why.
        */
        [[nodiscard]] static constexpr status_code unroutable(raw_uid_t raw_uid) noexcept;

        /**
        * @brief Ensures the project has at least one task somewhere.
        *
        * Three empty tiers is a manager that can do nothing at all - certainly a
        * mistake, and worth saying so here rather than letting it surface as a
        * confusing uid-type deduction failure.
        */
        static_assert(
            not (InstantTasks::is_empty() and
                 PolledTasks::is_empty() and
                 StatefulTasks::is_empty()),
            "task_manager requires at least one task in at least one tier."
        );

        /**
        * @brief No uid may be claimed by more than one tier.
        *
        * Each sub-manager already rejects duplicates *within* itself, but nothing
        * there can see across tiers - and a uid claimed twice would route to
        * whichever manager happened to be checked first, silently shadowing the
        * other task. The generator cannot emit this, but a hand-written task list
        * can.
        */
        static_assert(
            detail::tiers_are_disjoint_v<InstantTasks, PolledTasks, StatefulTasks>,
            "A task uid is claimed by more than one tier. Every uid must belong to "
            "exactly one of the instant, polled, or stateful task lists."
        );
    };

    /**
    * @brief The `task_manager` for three typelists of tasks.
    *
    * Bridges the generated task lists to the manager's form. This keeps the two
    * concerns apart exactly where a schema-driven project wants them: the task
    * **lists** are generated artifacts, while the manager **instantiation** stays
    * in hand-written config built from them - so regenerating never rewrites the
    * user's wiring, and the wiring never hard-codes the task set.
    *
    * @tparam InstantTasks  Typelist of instant commands.
    * @tparam PolledTasks   Typelist of polled tasks.
    * @tparam StatefulTasks Typelist of stateful tasks.
    */
    template<typename InstantTasks, typename PolledTasks, typename StatefulTasks>
    using task_manager_from_t = task_manager<InstantTasks, PolledTasks, StatefulTasks>;

} // namespace etask::core::managers

#include "task_manager.tpp"
#endif // ETASK_CORE_MANAGERS_TASK_MANAGER_HPP_
