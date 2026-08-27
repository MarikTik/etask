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
#include <etools/meta/typelist.hpp>
#include <etools/factories/dispatch_factory.hpp>
#include <etools/factories/utils/capacity.hpp>
#include <etools/memory/buffer_view.hpp>
#include <array>
#include <bitset>
#include <cstdint>
#include <vector>

namespace etask::core::managers {

    /**
    * @class polled_task_manager
    *
    * @brief Owns, executes, and concludes the project's @ref polled_task types.
    *
    * @tparam Tasks The polled task types this manager owns. A bare `Task`
    *         reserves one concurrent slot; `etools::factories::utils::capacity<Task, N>`
    *         reserves `N`. Bare and wrapped entries mix freely.
    */
    template<typename ...Tasks>
    class polled_task_manager {
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

        /// @brief Total concurrent slots reserved across all `Tasks`.
        static constexpr std::size_t total_capacity = (reg_t<Tasks>::count + ...);

        /// @brief `task_uid_t` normalized to its raw integral form.
        using raw_uid_t = detail::raw_uid_t<task_uid_t>;

    public:
        /**
        * @brief Constructs the manager, preallocating storage for concurrent tasks.
        *
        * @param max_task_load Expected maximum number of concurrently live tasks.
        *        Defaults to `total_capacity`, the true upper bound; a project that
        *        knows it runs fewer at once should say so and save the storage.
        */
        explicit polled_task_manager(std::size_t max_task_load = total_capacity);

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
        *         slots are all occupied; `task_unknown` when the uid matches no
        *         owned task or no constructor accepts `args`.
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
        *         already ending - a task concludes once.
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

        /// @brief Storage for every live task record.
        using tasks_container_t = std::vector<task_info>;

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
        std::bitset<total_capacity> _garbage;

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

} // namespace etask::core::managers

#include "polled_task_manager.tpp"
#endif // ETASK_CORE_MANAGERS_POLLED_TASK_MANAGER_HPP_
