// SPDX-License-Identifier: MIT
/**
* @file polled_task_manager.hpp
*
* @brief Declares `polled_task_manager`, which owns and drives tasks that run
*        across ticks but are never suspended.
*
* @ingroup etask_core etask::core::managers
*
* This is the middle of the three managers. It owns @ref polled_task instances
* (and @ref oneshot_task, which is one), constructs them by uid, calls
* `on_execute()` on each `update()` until `is_finished()` says stop, then hands
* the task to its channel to conclude.
*
* ## What it deliberately does not have
*
* No pause, no resume. A polled task has no `on_pause`/`on_resume` to call, so
* there is nothing to drive and no reason to carry the paused/resumed state that
* would track it. That removes two branches from the update loop and two flags
* from every task's state - see @ref stateful_task_manager, which is exactly
* this manager plus the suspension machinery.
*
* A task may still be **completed** early (`complete_task`): concluding a task
* does not require it to be suspendable.
*
* ## Not called directly
*
* User code talks to @ref task_manager, the façade that routes a uid to whichever
* of the three managers owns that tier. This class is the machinery behind it.
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
#ifndef ETASK_CORE_MANAGERS_POLLED_TASK_MANAGER_HPP_
#define ETASK_CORE_MANAGERS_POLLED_TASK_MANAGER_HPP_
#include "../channel.hpp"
#include "../status_code.hpp"
#include "../completion_reason.hpp"
// Both tiers this manager accepts: a plain polled task, and the oneshot task
// that is one with its completion predicate sealed.
#include "../tasks/polled_task.hpp"
#include "../tasks/oneshot_task.hpp"
#include "../tasks/stateful_task.hpp"
#include "detail/registry_traits.hpp"
#include "detail/registered_task.hpp"
#include "detail/payload_requirement.hpp"
#include <etools/meta/typelist.hpp>
#include <etools/factories/dispatch_factory.hpp>
#include <etools/factories/utils/capacity.hpp>
#include <etools/memory/buffer_view.hpp>
#include <etools/memory/static_vector.hpp>
#include <array>
#include <bitset>
#include <cstdint>

namespace etask::core::managers {

    /**
    * @class polled_task_manager
    *
    * @brief Owns, executes, and concludes the project's @ref polled_task types.
    *
    * ## Two caps, and why both exist
    *
    * A task type's own `capacity<Task, N>` bounds how many of *that* task may be
    * live. `Budget` bounds how many tasks may be live in this manager **at all**.
    * They answer different questions, and only the first is derivable from the
    * schema alone: nothing in a task's declaration says how many *other* tasks
    * run beside it.
    *
    * Without a budget the only sound bound is the sum of every per-task cap - the
    * state where every task runs at its own maximum simultaneously. That is
    * correct and almost always far too pessimistic; a device with four tasks
    * capped at four each reserves sixteen records to run, in practice, three.
    * `Budget` is where a project states the number it measured, and it is
    * enforced rather than advisory: storage is exactly `Budget` records, held
    * inline, and a registration beyond it is refused with
    * `status_code::task_budget_exhausted`.
    *
    * @note Deliberately no fairness policy. A budget below the sum of the caps
    *       means task types compete for the shared remainder, first-come
    *       first-served, and one greedy task can crowd out others. Which tasks
    *       actually coexist is a property of the application, not of the
    *       framework, so the manager does not guess: measure the real peak and
    *       set `Budget` from it.
    *
    * @tparam Budget Maximum number of concurrently live tasks. Defaults to the
    *         sum of every task's reserved slots - the true upper bound, and the
    *         only safe default when the project has not measured its own peak.
    * @tparam Tasks The polled task types this manager owns. A bare `Task`
    *         reserves one concurrent slot; `etools::factories::utils::capacity<Task, N>`
    *         reserves `N`. Bare and wrapped entries mix freely.
    *
    * @note `Budget` leads the parameter list because `Tasks` is a pack and must
    *       come last. Use @ref polled_task_manager_from_t to build one from a
    *       typelist without naming the order.
    */
    template<std::size_t Budget, typename ...Tasks>
    class polled_task_manager {
        static_assert(Budget > 0,
            "polled_task_manager requires Budget > 0: a manager that can never hold "
            "a live task cannot run one.");

        /**
        * @brief The stored form of a pack element: `capacity<Stored, N>`, where
        *        `Stored` is the task itself or the adapter that builds it from a
        *        wire payload.
        *
        * A generated task has a native-typed constructor, which the registry
        * cannot call with the request's `buffer_view`; @ref detail::registered_t
        * wraps it in @ref task_unpack_adapter so it can. Doing that here rather
        * than in the generated task list keeps construction a manager concern -
        * the list only ever names task types.
        */
        template<typename T>
        using reg_t = detail::registered_t<T>;

        /// @brief The declared (unwrapped, unadapted) task type of a pack element.
        template<typename T>
        using bare_t = typename etools::factories::utils::as_capacity_t<T>::type;

    public:
        /**
        * @typedef task_uid_t
        * @brief The task identifier type, taken from the owned tasks' `uid` members.
        */
        using task_uid_t = etools::meta::member_t<detail::uid_extractor, Tasks...>;

        /**
        * @typedef channel_t
        * @brief The channel type this manager delivers results through.
        */
        using channel_t = channel<task_uid_t>;

        /**
        * @var max_params_size
        *
        * @brief Payload bytes the largest of these tasks needs for its arguments.
        *
        * The schema's demand on a request packet, over and above the directive
        * byte and the uid. A channel compares this against what its packet
        * actually carries; see @ref detail::payload_requirement.hpp for why an
        * unchecked mismatch is silent rather than loud.
        */
        static constexpr std::size_t max_params_size = detail::max_params_size_v<Tasks...>;

    private:
        /// @brief The polymorphic base this manager owns its tasks through.
        using task_t = polled_task<task_uid_t>;

        /**
        * @brief Zero-allocation factory constructing a task by raw uid.
        *
        * Registered on the *stored* forms (`reg_t<Tasks>`), not the declared
        * ones: a native-ctor task reaches the registry as the adapter that can
        * build it from a payload. The adapter inherits `Task::uid`, so uid
        * routing is unchanged, and it is-a `Task` is-a `task_t`, so the base
        * the factory hands back is the same.
        */
        using registry_t = etools::factories::dispatch_factory<task_t, detail::raw_uid_extractor, reg_t<Tasks>...>;

        /// @brief Total concurrent slots reserved across all `Tasks`; the ceiling `Budget` may not exceed.
        static constexpr std::size_t total_capacity = (reg_t<Tasks>::count + ...);

        /// @brief `task_uid_t` normalized to its raw integral form.
        using raw_uid_t = detail::raw_uid_t<task_uid_t>;

    public:
        /**
        * @brief Constructs the manager.
        *
        * Storage for `Budget` live-task records is embedded in the manager and needs
        * no preparation, so there is nothing to size here and nothing to allocate.
        */
        polled_task_manager() noexcept = default;

        /// @brief Deleted copy constructor - `registry_t` owns task storage in place and cannot be relocated.
        polled_task_manager(const polled_task_manager&) = delete;
        /// @brief Deleted copy assignment - see the deleted copy constructor.
        polled_task_manager& operator=(const polled_task_manager&) = delete;
        /// @brief Deleted move constructor - see the deleted copy constructor.
        polled_task_manager(polled_task_manager&&) = delete;
        /// @brief Deleted move assignment - see the deleted copy constructor.
        polled_task_manager& operator=(polled_task_manager&&) = delete;

        /**
        * @brief Constructs a task of type `uid` and takes ownership of it.
        *
        * Arguments are perfectly forwarded to the matched task's constructor, so
        * each task type may impose its own signature.
        *
        * @tparam Args Task constructor argument types.
        *
        * @param origin       Channel that will receive this task's result. Not owned.
        * @param initiator_id Id of the device or component that asked for the task.
        * @param uid          Which task type to construct.
        * @param args         Forwarded to that task type's constructor.
        *
        * @return `ok` on success; `channel_null` for a null channel;
        *         `duplicate_task` / `task_limit_reached` when this uid's reserved
        *         slots are all occupied (the first when it reserves one slot, the
        *         second when it reserves several); `task_budget_exhausted` when the
        *         manager itself is full, so no task of any type can start until one
        *         concludes; `task_unknown` when the uid matches no owned task or no
        *         constructor accepts `args`; `reentrancy_conflict` when called from
        *         inside a lifecycle hook (see @ref update).
        *
        * @note The per-uid check runs before the tier's, so when both are spent at
        *       the same registration the per-uid code is what the caller sees. A uid
        *       whose `concurrency` equals `Budget` therefore never reports
        *       `task_budget_exhausted`, and acting on the code it does get - raising
        *       that task's concurrency - will not help, because the tier was the
        *       binding constraint. Keep each uid's reserved slots strictly below
        *       `Budget` to keep the two diagnoses distinguishable; nothing enforces
        *       it. See `integration/bombardment`.
        */
        template<typename... Args>
        [[nodiscard]] status_code register_task(channel_t *origin, std::uint8_t initiator_id, task_uid_t uid, Args&&... args);

        /**
        * @brief Forces a running task to conclude before it would on its own.
        *
        * Marks the task; on the next `update()` its `on_complete(reason)` runs
        * with the supplied reason and the task is removed.
        *
        * @param uid    Which running task to conclude.
        * @param reason Why. Never `completion_reason::finished`, which is reserved
        *               for natural completion.
        *
        * @return `ok`; `invalid_completion_reason` for `finished`;
        *         `task_not_registered` if no such task is running;
        *         `task_already_finished` / `task_already_concluding` if it is
        *         already ending - a task concludes once; `reentrancy_conflict` when
        *         called from inside a lifecycle hook (see @ref update).
        */
        [[nodiscard]] status_code complete_task(task_uid_t uid, completion_reason reason);

        /**
        * @brief Runs one cycle over every owned task.
        *
        * For each: concludes it if it was aborted or reports itself finished,
        * otherwise gives it one `on_execute()`. Concluded tasks are removed at the
        * end of the cycle.
        *
        * Call periodically from the application's main loop.
        *
        * ## Cost
        *
        * Linear in the number of *live* tasks, plus a small floor that scales with
        * `Budget` rather than with occupancy: the cycle clears a
        * `std::bitset<Budget>` and sweeps that range whether or not the slots hold
        * anything. So an unused slot is cheap but not free.
        *
        * Measured on an ESP32-D0WD-V3 at 240 MHz, `-O2`, with a one-store task body
        * (`bench/RESULTS.md` §3b, §3d, §3e):
        *
        * | | |
        * |---|---|
        * | Marginal cost per live task | ~542 ns, linear to within 2 ns over 0-32 |
        * | Framework share of one tick | ~616 ns over a hand-written loop doing the same work |
        * | Idle floor, `Budget` = 1 | ~114 ns |
        * | Idle floor, `Budget` = 128 | ~325 ns |
        *
        * The budget floor is sub-linear - 128x the slots for under 3x the floor -
        * because the bitset clears a word at a time. Size `Budget` for the measured
        * peak; over-declaring costs RAM (~36 B per record) far more than it costs
        * time.
        *
        * @warning **Not reentrant.** A task's lifecycle hook must not call back into
        *          this manager: `register_task` and `complete_task` invoked from
        *          `on_execute()` or `on_complete()` are refused with
        *          `status_code::reentrancy_conflict` rather than mutating the record
        *          set mid-sweep. Storage never relocates, so such a call could not
        *          corrupt memory, but it could still make this cycle visit a task
        *          twice or not at all - so it is rejected outright instead.
        *          A hook that wants to start follow-on work should record the
        *          intent and act on it after `update()` returns.
        */
        void update();

        /**
        * @brief Whether this manager owns the task type identified by `uid`.
        *
        * The façade's routing predicate: a uid belongs to exactly one manager, and
        * this answers for this one. Constant-expression evaluable, so the façade's
        * dispatch costs nothing at runtime.
        *
        * @param raw_uid Raw uid to test.
        * @return `true` if some owned task declares this uid.
        */
        [[nodiscard]] static constexpr bool owns(raw_uid_t raw_uid) noexcept;

    private:
        /**
        * @struct task_info
        * @brief Everything the manager needs to drive one live task and deliver its result.
        */
        struct task_info {
            /**
            * @brief Constructs a fully-initialized record.
            *
            * @param task_in         Owning handle from `registry_t::emplace`.
            * @param initiator_id_in Id of the requester that asked for the task.
            * @param uid_in          The task type's unique identifier.
            * @param channel_in      Channel results are delivered through; must
            *                        outlive this record. Not owned.
            */
            task_info(
                typename registry_t::handle_t&& task_in,
                std::uint8_t initiator_id_in,
                task_uid_t uid_in,
                channel_t* channel_in) noexcept;

            /**
            * @brief Owning handle to the task.
            *
            * Dropping it destroys the task in its registry slot and frees the slot
            * for reuse, so losing a `task_info` without erasing it leaks the slot.
            */
            typename registry_t::handle_t task;

            /// @brief Id of the component that initiated the task; travels back with the result.
            std::uint8_t initiator_id;

            /// @brief The task type's unique identifier; routes the result.
            task_uid_t uid;

            /// @brief Where the result goes. Not owned; must outlive this record.
            channel_t* channel;

            /**
            * @brief The reason `on_complete` will be invoked with, and the whole
            *        of this task's lifecycle state.
            *
            * `completion_reason::finished` while the task is running its course;
            * `complete_task` overwrites it to conclude the task early. Since
            * `finished` is framework-only and `complete_task` rejects it outright,
            * anything other than `finished` here means the task has been marked to
            * conclude - there is no separate flag that could disagree with it.
            *
            * *Which* other reason still matters, and is not collapsed away:
            * `aborted` is an immediate termination, while a caller-supplied reason
            * is an early but orderly conclusion. They report different statuses on
            * the wire - see @ref reply_status.
            *
            * A polled task has no pause/resume state to track, so this single field
            * is all the state there is; there is no `core::state` here.
            */
            completion_reason reason = completion_reason::finished;
        };

        /**
        * @brief The status a concluding task's reply carries, from why it concluded.
        *
        * The manager names this explicitly rather than leaving it implicit: a peer
        * reads the status byte to know what it received, and the three ways a task
        * can end are genuinely different events.
        *
        * - `finished` -> `task_finished` : ran its course.
        * - `aborted`  -> `task_aborted`  : terminated immediately, mid-work.
        * - user reason -> `task_completed_early` : concluded before it would have,
        *   but in an orderly way. The reason byte carries which.
        *
        * A task may still override this from `on_complete` via
        * `outcome::with_status(code)`; this is the default it starts from.
        *
        * @param reason Why the task is concluding.
        * @return The status code for its reply.
        */
        [[nodiscard]] static constexpr status_code reply_status(completion_reason reason) noexcept;

        /**
        * @brief Storage for every live task record.
        *
        * Fixed at `Budget` records, held inline: no heap, and no reallocation, so a
        * record's address is stable for its whole lifetime. `update()` relies on
        * that - it holds a reference to a record across the task's own lifecycle
        * hooks, which a growing container could invalidate underneath it.
        */
        using tasks_container_t = etools::memory::static_vector<task_info, Budget>;

        /// @brief Mutable iterator over @ref tasks_container_t.
        using task_iterator = typename tasks_container_t::iterator;

        /**
        * @brief The task factory.
        *
        * @note Declared before `_tasks` deliberately. Each `registry_t::handle_t`
        *       holds a pointer back into this registry, and members are destroyed
        *       in reverse declaration order - so the registry outlives every handle
        *       in `_tasks`. Reordering these two reintroduces a dangling pointer
        *       at destruction.
        */
        registry_t _registry;

        /// @brief Records for all currently live tasks.
        tasks_container_t _tasks;

        /// @brief Marks which `_tasks` entries concluded this cycle and must be erased.
        std::bitset<Budget> _garbage;

        /**
        * @brief Whether a sweep is in progress, so mutations must be refused.
        *
        * Set for the duration of @ref update. Every entry point that would add or
        * mark a record consults it, which is what gives
        * `status_code::reentrancy_conflict` its meaning.
        */
        bool _in_update = false;

        /**
        * @struct update_guard
        * @brief Sets `_in_update` for a scope and clears it on the way out.
        *
        * A scope guard rather than a plain assignment pair so the flag is cleared
        * even if a task's hook exits by throwing - otherwise one escaping exception
        * would leave the manager permanently refusing every registration.
        */
        struct update_guard {
            /// @brief The flag to hold set; cleared when this guard is destroyed.
            bool& flag;

            /// @brief Marks the sweep as active.
            explicit update_guard(bool& flag_in) noexcept : flag{flag_in} { flag = true; }

            /// @brief Marks the sweep as finished.
            ~update_guard() noexcept { flag = false; }

            update_guard(const update_guard&) = delete;
            update_guard& operator=(const update_guard&) = delete;
        };

        /**
        * @brief Finds the live record for `uid`.
        *
        * @param uid The task type to look for.
        * @return Iterator to the record, or `_tasks.end()`.
        *
        * @warning Invalidated by any structural change to `_tasks`, including an
        *          `update()` that erases concluded tasks.
        */
        [[nodiscard]] task_iterator find(task_uid_t uid) noexcept;

        /**
        * @brief How many concurrent instances of `raw_uid` may be live at once.
        *
        * @param raw_uid Raw uid to look up.
        * @return The reserved slot count, or `0` if this manager does not own it.
        */
        [[nodiscard]] static constexpr std::size_t capacity_of(raw_uid_t raw_uid) noexcept;

        /// @brief A manager with no tasks is certainly a mistake.
        static_assert(sizeof...(Tasks) > 0, "polled_task_manager requires at least one task type.");

        /// @brief Every task must carry a `static constexpr uid`.
        static_assert((etools::meta::has_static_member_variable_uid_v<bare_t<Tasks>> && ...),
            "All tasks must have a static member 'uid' to uniquely identify them.");

        /// @brief Every `capacity<Task, N>` must reserve at least one slot.
        static_assert(((reg_t<Tasks>::count > 0) && ...),
            "capacity<Task, N> requires N > 0 for every task type.");

        /**
        * @brief A budget above the sum of the per-task caps reserves storage nothing can fill.
        *
        * Every live task occupies one of its own type's reserved slots, so at most
        * `total_capacity` tasks can exist at once no matter how large the budget
        * is. Anything beyond that is records that can never be used - a statement
        * of intent the type system can see is unachievable, and much more likely a
        * miscount than a deliberate choice.
        */
        static_assert(Budget <= total_capacity,
            "Budget exceeds the sum of the per-task concurrency limits, so the extra "
            "slots can never be occupied. Lower the tier's budget, or raise a task's "
            "capacity<Task, N>.");

        /// @brief Checked on the underlying types, so `Task` and `capacity<Task, N>` count as one.
        static_assert(etools::meta::is_distinct_v<bare_t<Tasks>...>,
            "All task types must be distinct.");

        /**
        * @brief No two task types may share a uid *value*.
        *
        * Type-distinctness cannot catch this: two different classes can each
        * declare `uid = 5`, and the registry has no way to route one wire uid to
        * two constructors.
        */
        static_assert(
            etools::meta::all_distinct_fast(std::array<raw_uid_t, sizeof...(Tasks)>{
                detail::raw_uid_extractor<bare_t<Tasks>>::value...
            }),
            "All tasks must have pairwise-distinct uid values, even if they are different C++ types."
        );

        /**
        * @brief Every task here must actually be a polled task.
        *
        * This is the tier check that makes the split mean something: a
        * @ref stateful_task routed here would never have its `on_pause`/
        * `on_resume` driven, and an @ref instant_task does not belong to this
        * hierarchy at all.
        */
        static_assert((std::is_base_of_v<task_t, bare_t<Tasks>> && ...),
            "All tasks in a polled_task_manager must derive from polled_task<uid_t>. "
            "A stateful_task belongs in stateful_task_manager; an instant_task in "
            "instant_task_manager.");

        /**
        * @brief ...and must not be a *stateful* task.
        *
        * `stateful_task` derives from `polled_task`, so the `is_base_of` check
        * above accepts one - and this manager would then drive its execution while
        * never calling `on_pause`/`on_resume`, and the façade would answer
        * `task_not_pausable` for a task that plainly implements pausing. The task
        * would look suspendable and silently not be, which is precisely the
        * failure the tier split exists to eliminate. Only the exact tier belongs
        * here.
        */
        static_assert(
            (not std::is_base_of_v<stateful_task<task_uid_t>, bare_t<Tasks>> && ...),
            "A stateful_task cannot be managed by polled_task_manager: its "
            "on_pause()/on_resume() would never be called. List it in the stateful "
            "task list instead.");
    };

    /**
    * @brief The default budget for a pack of tasks: the sum of their reserved slots.
    *
    * The bound that holds without knowing anything about the application. Named
    * here so a caller can write it explicitly, or compare a measured budget
    * against it.
    *
    * @tparam Tasks A manager's task pack.
    */
    template<typename... Tasks>
    inline constexpr std::size_t default_polled_budget = detail::sum_of_capacities_v<Tasks...>;

} // namespace etask::core::managers

#include "polled_task_manager.tpp"
#endif // ETASK_CORE_MANAGERS_POLLED_TASK_MANAGER_HPP_
