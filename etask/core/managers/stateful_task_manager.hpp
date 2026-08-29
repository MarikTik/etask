// SPDX-License-Identifier: MIT
/**
* @file stateful_task_manager.hpp
*
* @brief Declares `stateful_task_manager`, which owns and drives tasks that can
*        be suspended and resumed.
*
* @ingroup etask_core etask::core::managers
*
* This is @ref polled_task_manager plus suspension. It owns @ref stateful_task
* instances, runs the same execute-until-finished loop, and additionally honors
* pause and resume directives - calling `on_pause()` when a running task is
* suspended and `on_resume()` when it comes back, each exactly once per
* transition.
*
* ## The extra cost, stated plainly
*
* Suspension is not free: every record carries a @ref detail::state byte, `update()`
* carries the branches that act on it, and every task pays two vtable slots for
* hooks it must implement. That is the whole reason the tiers are separate - a
* task that cannot be paused should not be paying for any of it, and belongs in
* @ref polled_task_manager.
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
#ifndef ETASK_CORE_MANAGERS_STATEFUL_TASK_MANAGER_HPP_
#define ETASK_CORE_MANAGERS_STATEFUL_TASK_MANAGER_HPP_
#include "../channel.hpp"
#include "../status_code.hpp"
#include "../completion_reason.hpp"
#include "../tasks/stateful_task.hpp"
#include "detail/registry_traits.hpp"
#include "detail/registered_task.hpp"
#include "detail/payload_requirement.hpp"
#include "detail/state.hpp"
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
    * @class stateful_task_manager
    *
    * @brief Owns, executes, suspends, and concludes the project's
    *        @ref stateful_task types.
    *
    * ## Two caps, and why both exist
    *
    * As @ref polled_task_manager: a task's own `capacity<Task, N>` bounds how many
    * of *that* task may be live, while `Budget` bounds how many tasks may be live
    * in this manager at all. The default is the sum of the per-task caps - the
    * true upper bound, and the only safe assumption before a project has measured
    * its own peak. Storage is exactly `Budget` records, held inline; a
    * registration beyond it is refused with `status_code::task_budget_exhausted`.
    *
    * A suspended task still holds its record, so a tier whose tasks spend long
    * stretches paused reaches its budget sooner than execution time alone would
    * suggest.
    *
    * @tparam Budget Maximum number of concurrently live tasks, running or
    *         suspended. Defaults to the sum of every task's reserved slots.
    * @tparam Tasks The stateful task types this manager owns. A bare `Task`
    *         reserves one concurrent slot; `etools::factories::utils::capacity<Task, N>`
    *         reserves `N`. Bare and wrapped entries mix freely.
    *
    * @note `Budget` leads the parameter list because `Tasks` is a pack and must
    *       come last.
    */
    template<std::size_t Budget, typename ...Tasks>
    class stateful_task_manager {
        static_assert(Budget > 0,
            "stateful_task_manager requires Budget > 0: a manager that can never hold "
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
        using task_t = stateful_task<task_uid_t>;

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
        stateful_task_manager() noexcept = default;

        /// @brief Deleted copy constructor - `registry_t` owns task storage in place and cannot be relocated.
        stateful_task_manager(const stateful_task_manager&) = delete;
        /// @brief Deleted copy assignment - see the deleted copy constructor.
        stateful_task_manager& operator=(const stateful_task_manager&) = delete;
        /// @brief Deleted move constructor - see the deleted copy constructor.
        stateful_task_manager(stateful_task_manager&&) = delete;
        /// @brief Deleted move assignment - see the deleted copy constructor.
        stateful_task_manager& operator=(stateful_task_manager&&) = delete;

        /**
        * @brief Constructs a task of type `uid` and takes ownership of it.
        *
        * Arguments are perfectly forwarded to the matched task's constructor.
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
        *         slots are all occupied; `task_budget_exhausted` when the manager
        *         itself is full, so no task of any type can start until one
        *         concludes; `task_unknown` when the uid matches no owned task or no
        *         constructor accepts `args`; `reentrancy_conflict` when called from
        *         inside a lifecycle hook (see @ref update).
        */
        template<typename... Args>
        [[nodiscard]] status_code register_task(channel_t *origin, std::uint8_t initiator_id, task_uid_t uid, Args&&... args);

        /**
        * @brief Suspends a running task.
        *
        * Takes effect on the next `update()`, which runs the task's `on_pause()`
        * and stops executing it until it is resumed or completed.
        *
        * @param uid Which running task to suspend.
        *
        * @return `ok`; `task_not_registered` if no such task is running;
        *         `task_already_paused` if it is already suspended or about to be;
        *         `task_already_finished` / `task_already_concluding` if it is
        *         already ending - a concluding task is past pausing;
        *         `reentrancy_conflict` when called from inside a lifecycle hook.
        */
        [[nodiscard]] status_code pause_task(task_uid_t uid);

        /**
        * @brief Resumes a suspended task.
        *
        * Takes effect on the next `update()`, which runs the task's `on_resume()`
        * and returns it to execution.
        *
        * @param uid Which suspended task to resume.
        *
        * @return `ok`; `task_not_registered` if no such task is running;
        *         `task_already_running` if it was never suspended;
        *         `task_already_resumed` if a resume is already pending;
        *         `task_already_finished` / `task_already_concluding` if it is
        *         already ending; `reentrancy_conflict` when called from inside a
        *         lifecycle hook.
        */
        [[nodiscard]] status_code resume_task(task_uid_t uid);

        /**
        * @brief Forces a task to conclude before it would on its own.
        *
        * Works regardless of whether the task is running or suspended: concluding
        * is not gated on the run state. On the next `update()` its
        * `on_complete(reason)` runs and the task is removed.
        *
        * @param uid    Which task to conclude.
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
        * For each, in priority order: concludes it if it is ending; otherwise
        * services a pending pause or resume (firing `on_pause()`/`on_resume()`
        * once); otherwise, if running, gives it one `on_execute()`. A suspended
        * task with nothing pending is left alone. Concluded tasks are removed at
        * the end of the cycle.
        *
        * Call periodically from the application's main loop.
        *
        * @warning **Not reentrant.** A task's lifecycle hook must not call back into
        *          this manager: `register_task`, `pause_task`, `resume_task`, and
        *          `complete_task` invoked from `on_execute()`, `on_pause()`,
        *          `on_resume()`, or `on_complete()` are refused with
        *          `status_code::reentrancy_conflict` rather than mutating the record
        *          set mid-sweep. Storage never relocates, so such a call could not
        *          corrupt memory, but it could still make this cycle visit a task
        *          twice or not at all - so it is rejected outright instead.
        */
        void update();

        /**
        * @brief Whether this manager owns the task type identified by `uid`.
        *
        * The façade's routing predicate. Constant-expression evaluable, so the
        * façade's dispatch costs nothing at runtime.
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
            * for reuse.
            */
            typename registry_t::handle_t task;

            /// @brief Id of the component that initiated the task; travels back with the result.
            std::uint8_t initiator_id;

            /// @brief The task type's unique identifier; routes the result.
            task_uid_t uid;

            /// @brief Where the result goes. Not owned; must outlive this record.
            channel_t* channel;

            /**
            * @brief The reason `on_complete` will be invoked with, and the record's
            *        "is it ending" state.
            *
            * `completion_reason::finished` while the task is running its course;
            * `complete_task` overwrites it to conclude the task early. Anything
            * other than `finished` means the task is ending. Which other reason
            * still matters and is not collapsed - see @ref reply_status.
            */
            completion_reason reason = completion_reason::finished;

            /// @brief Where the task sits on the running/suspended axis.
            detail::state state = detail::state::running;
        };

        /**
        * @brief The status a concluding task's reply carries, from why it concluded.
        *
        * The manager names this explicitly rather than leaving it implicit:
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
        * @note Declared before `_tasks` deliberately: each handle in `_tasks` holds
        *       a pointer back into this registry, and reverse-order member
        *       destruction means the registry outlives them all. Reordering these
        *       two reintroduces a dangling pointer at destruction.
        */
        registry_t _registry;

        /// @brief Records for all currently live tasks.
        tasks_container_t _tasks;

        /// @brief Marks which `_tasks` entries concluded this cycle and must be erased.
        std::bitset<Budget> _garbage;

        /**
        * @brief Whether a sweep is in progress, so mutations must be refused.
        *
        * Set for the duration of @ref update. Every entry point that would add a
        * record or change one's state consults it, which is what gives
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
        * @warning Invalidated by any structural change to `_tasks`.
        */
        [[nodiscard]] task_iterator find(task_uid_t uid) noexcept;

        /**
        * @brief Rejects a directive aimed at a task that is already ending.
        *
        * The precondition `pause_task`, `resume_task`, and `complete_task` all
        * share: a task that has finished or been marked to conclude is past taking
        * further direction.
        *
        * @param info The record to test.
        * @return `status_code::ok` if the task can still be directed, otherwise the
        *         code explaining why not.
        */
        [[nodiscard]] static status_code reject_if_ending(task_info& info);

        /**
        * @brief How many concurrent instances of `raw_uid` may be live at once.
        *
        * @param raw_uid Raw uid to look up.
        * @return The reserved slot count, or `0` if this manager does not own it.
        */
        [[nodiscard]] static constexpr std::size_t capacity_of(raw_uid_t raw_uid) noexcept;

        /// @brief A manager with no tasks is certainly a mistake.
        static_assert(sizeof...(Tasks) > 0, "stateful_task_manager requires at least one task type.");

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
        * is. Anything beyond that is records that can never be used.
        */
        static_assert(Budget <= total_capacity,
            "Budget exceeds the sum of the per-task concurrency limits, so the extra "
            "slots can never be occupied. Lower the tier's budget, or raise a task's "
            "capacity<Task, N>.");

        /// @brief Checked on the underlying types, so `Task` and `capacity<Task, N>` count as one.
        static_assert(etools::meta::is_distinct_v<bare_t<Tasks>...>,
            "All task types must be distinct.");

        /// @brief No two task types may share a uid *value*, even as different C++ types.
        static_assert(
            etools::meta::all_distinct_fast(std::array<raw_uid_t, sizeof...(Tasks)>{
                detail::raw_uid_extractor<bare_t<Tasks>>::value...
            }),
            "All tasks must have pairwise-distinct uid values, even if they are different C++ types."
        );

        /**
        * @brief Every task here must actually be a stateful task.
        *
        * A @ref polled_task routed here has no `on_pause`/`on_resume` to drive, so
        * it would accept a pause directive and then not honor it - exactly the
        * silent no-op the tier split exists to eliminate.
        */
        static_assert((std::is_base_of_v<task_t, bare_t<Tasks>> && ...),
            "All tasks in a stateful_task_manager must derive from stateful_task<uid_t>. "
            "A task that cannot be paused belongs in polled_task_manager.");
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
    inline constexpr std::size_t default_stateful_budget = detail::sum_of_capacities_v<Tasks...>;

} // namespace etask::core::managers

#include "stateful_task_manager.tpp"
#endif // ETASK_CORE_MANAGERS_STATEFUL_TASK_MANAGER_HPP_
