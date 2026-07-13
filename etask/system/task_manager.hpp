// SPDX-License-Identifier: BSL-1.1
/**
* @file task_manager.hpp 
*
* @brief Declares the `task_manager` class for managing task lifecycles, state transitions, and result dispatch in the etask framework.
*
* @ingroup etask_system etask::system
*
* This header defines the core management component of the etask system responsible for:
* - registering tasks dynamically
* - handling task state transitions
* - orchestrating task execution
* - delivering results via communication channels
*
* The file includes all declarations for the `task_manager` template class and its associated types,
* enabling integration of user-defined tasks into the etask framework's runtime environment.
*
* @section design_notes Design notes
*
* - @b Start-first policy:
*   Each task’s `on_start()` is invoked exactly once before any other lifecycle callback.
*   A single-shot task may therefore both start and finish in the same update tick.
*
* - @b Sticky resumed:
*   The `resumed` flag is an informational edge that stays set after a resume and is
*   typically cleared by a later pause. While running, `on_resume()` does not re-fire
*   because the manager gates it on `resumed && idle`.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-09
*
*opyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_SYSTEM_TASK_MANAGER_HPP_
#define ETASK_SYSTEM_TASK_MANAGER_HPP_
#include "channel.hpp"
#include "task.hpp"
#include "state.hpp"
#include "status_code.hpp"
#include <etools/meta/info_gen.hpp>
#include <etools/meta/traits.hpp>
#include <etools/meta/typelist.hpp>
#include <etools/memory/buffer_view.hpp>
#include <etools/factories/dispatch_factory.hpp>
#include <etools/factories/utils/capacity.hpp>
#include <vector>
#include <bitset>

generate_has_static_member_variable(uid) ///< Macro to create a type trait for task unique identifier compile time check.

namespace etask::system {
    
    /**
    *lass task_manager
    *
    * @brief Manages the lifecycle, execution, and state transitions of tasks in the etask framework.
    *
    * The `task_manager` class provides a flexible, runtime mechanism for orchestrating task execution,
    * including registering new tasks, controlling their states, and dispatching results through
    * communication channels.
    *
    * Tasks managed by this class must:
    * - inherit from `etask::system::task`
    * - define a static member `uid` that uniquely identifies the task type
    *
    * The manager maintains an internal table of known task types, allowing efficient instantiation
    * and control of tasks purely via their UID values.
    *
    * Responsibilities
    * 
    *   - Registering new task instances at runtime
    * 
    *   - Maintaining task states (started, paused, resumed, aborted, finished)
    * 
    *   - Calling appropriate lifecycle methods on tasks (start, execute, complete, pause, resume)
    * 
    *   - Cleaning up completed or aborted tasks
    * 
    *   - Forwarding task results through a `channel` abstraction
    *
    * @tparam Tasks Variadic list of all supported task types to be managed at runtime.
    *               A bare `Task` reserves one concurrent slot; wrap it in
    *               `etools::factories::utils::capacity<Task, N>` to reserve `N`
    *               concurrent slots for that task type. Bare and wrapped entries
    *               may be mixed freely, exactly as `dispatch_factory` accepts.
    */
    template<typename ...Tasks>
    class task_manager {
        /**
        * @typedef reg_t
        * @brief The normalised `capacity<Task, N>` for a `Tasks` pack element `T`.
        *
        * `reg_t<T>::type` is the underlying bare task type; `reg_t<T>::count` is
        * its reserved concurrent slot count (1 for bare pack elements). Delegates
        * to `etools::factories::utils::as_capacity_t`, the same public primitive
        * `dispatch_factory` itself normalises through, so this can never drift
        * from the registry's own notion of "bare vs. capacity-tagged".
        *
        * @tparam T A bare task type or a `capacity<Task, N>` tag.
        */
        template<typename T>
        using reg_t = etools::factories::utils::as_capacity_t<T>;

        /**
        * @struct uid_extractor
        * @brief Metafunction that exposes a task type's uid exactly as declared.
        *
        * This trait forwards T::uid without normalization. It is useful when you
        * need to preserve the original uid type (e.g., a strongly-typed enum class)
        * for APIs that traffic in the semantic UID type rather than a raw integer.
        *
        * @tparam T A bare task type or a `capacity<Task, N>` tag; unwrapped via
        *           `reg_t<T>::type` before reading `uid`.
        *
        * #### Provided constants
        * - value : `T::uid` (exact type and value)
        *
        * @see raw_uid_extractor for a normalized, integral form of uid.
        */
        template<typename T> struct uid_extractor{
            static constexpr auto value = reg_t<T>::type::uid;
        };

        /**
        * @struct raw_uid_extractor
        * 
        * @brief Metafunction that normalizes a task type's uid to a raw integral type.
        *
        * This trait reads `T::uid`, strips cv-qualifiers from its type, and—if it is an
        * enumeration—converts it lazily to its underlying integral type. The resulting
        * value is a constant expression of the normalized integral type, suitable
        * for use in hashing tables and array indices (e.g., as keys in
        * static_factory 's registry).
        *
        * @tparam T Task type that exposes static constexpr uid.
        *
        * #### Requirements
        * 
        * - T must have a static constexpr member named uid.
        * - `decltype(T::uid)` must be either an integral type or an enum whose
        *   underlying type is integral.
        *
        * #### Provided aliases
        * 
        * - uid_cv_t : the exact declared type of `T::uid` (may be cv-qualified)
        * - uid_t    : uid_cv_t with cv removed
        * - raw_t    : uid_t if integral, otherwise std::underlying_type_t<uid_t>
        *
        * #### Provided constants
        * - value : static_cast<raw_t>(T::uid)
        *
        * @note This metafunction is intended for places that require a *numeric* key
        *       (e.g., MPH tables). It does not change the semantic value, only its type.
        */
        template<typename T> struct raw_uid_extractor{ 
            using uid_cv_t = decltype(T::uid);
            using uid_t = std::remove_cv_t<uid_cv_t>;

            using raw_t = typename std::conditional_t<
                std::is_enum_v<uid_t>,
                std::underlying_type<uid_t>,           // trait (lazy)
                etools::meta::type_identity<uid_t>     // trait (lazy)
            >::type;

            static_assert(
                std::is_integral_v<raw_t>,
                "uid must be an integral type or an enum with an integral underlying type"
            );

            static constexpr auto value = static_cast<raw_t>(T::uid); 
        };

        /** @typedef task_uid_t
        *
        * @brief Type representing the unique identifier for tasks.
        *
        * This is derived automatically from the template parameter pack `Tasks`.
        * The type is usually an enumeration or an integral type used to identify tasks uniquely.
        */ 
        using task_uid_t = etools::meta::member_t<uid_extractor, Tasks...>;

        /**
        * @typedef task_t
        *
        * @brief Type alias for the base task type used in this manager.
        *
        * Represents the common base class for all tasks, derived from
        * `task_uid_t` in the specialization of `task`.
        */
        using task_t = task<task_uid_t>;

        /**
        * @typedef channel_t
        * 
        * @brief Type alias for the communication channel used to deliver task results.
        * 
        * This type is a specialization of the `channel` class template,
        * parameterized with the `task_uid_t` type.
        * The channel is used to send results back to the originator of the task.
        * 
        * @note The channel must implement the `on_result` method to handle task results.
        */
        using channel_t = channel<task_uid_t>;

        /**
        * @typedef registry_t
        *
        * @brief Type of the compile-time task registry.
        *
        * A zero-allocation factory that constructs a `Tasks...` member by its raw
        * uid, owning the storage for each type's slots in place. `emplace()`
        * returns an owning `registry_t::handle_t`; dropping that handle destroys
        * the task in its slot and frees the slot for reuse.
        *
        * @see etools::factories::dispatch_factory
        */
        using registry_t = etools::factories::dispatch_factory<task_t, raw_uid_extractor, Tasks...>;

        /**
        * @brief Total number of concurrent task slots reserved across all `Tasks`.
        *
        * The sum of each pack element's reserved slot count (`reg_t<Tasks>::count`;
        * 1 for bare task types). This is the true upper bound on how many task
        * instances can be alive in `_tasks` at once, and replaces `sizeof...(Tasks)`
        * (a count of *types*, not of reservable *slots*) for sizing purposes.
        */
        static constexpr std::size_t total_capacity = (reg_t<Tasks>::count + ...);

        /**
        * @typedef raw_uid_t
        *
        * @brief `task_uid_t` normalized to a raw integral type (its underlying
        *        type if `task_uid_t` is an enum, otherwise `task_uid_t` itself).
        *
        * The registry keys, and `capacity_of`'s lookup, operate on this raw form.
        */
        using raw_uid_t = typename std::conditional_t<
            std::is_enum_v<task_uid_t>,
            std::underlying_type<task_uid_t>,
            etools::meta::type_identity<task_uid_t>
        >::type;
    public:
        /**
        * @brief Constructs the task manager with an optional maximum task load.
        *
        * @param max_task_load Expected maximum number of tasks to be managed concurrently.
        *                      Used to preallocate storage for efficiency.
        * 
        * @warning The default number of concurrently running tasks is equal
        *          to `total_capacity` (the sum of every task type's reserved
        *          slot count; 1 per bare task type, `N` for a `capacity<Task, N>`
        *          tag). It would be advised to specify a smaller load based on
        *          the project requirements. For `total_capacity` <= 255, there
        *          are no huge implications though.
        */
        task_manager(std::size_t max_task_load = total_capacity);

        /**
        * @brief Registers a new task for execution.
        *
        * This method looks up the task type associated with the given UID in the
        * compile-time registry and attempts to construct it in-place. The provided
        * arguments are perfectly forwarded to the constructor of the matched task
        * type. This allows defining custom constructors per task type, including
        * those with specific parameter constraints or overloads.
        *
        * If a task with the same UID is already registered, the call fails with
        * a duplicate status. If the UID does not correspond to any known task
        * type or the provided arguments do not match any constructor of the
        * corresponding task, the call fails with an unknown-task status.
        *
        * @tparam Args Variadic template parameter pack for task constructor arguments.
        *
        * @param origin Pointer to the channel that will receive the task's result.
        * @param initiator_id Identifier of the device or component that initiated the task.
        * @param uid Unique identifier of the task type to instantiate.
        * @param args Arguments perfectly forwarded to the constructor of the task.
        *
        * @return Status code indicating the outcome:
        *         - ok if the task was successfully registered
        *         - channel_null if the provided channel is null
        *         - duplicate_task if a task with the same UID already exists
        *         - task_unknown if the UID is not found or the constructor signature does not match
        *
        * @note This mechanism enables expansion of task construction semantics,
        *       since different task types can impose their own constructor constraints.
        */
        template<typename... Args>
        [[nodiscard]] status_code register_task(channel_t *origin, uint8_t initiator_id, task_uid_t uid, Args&&... args);

        /**
        * @brief Pauses the specified task, if it exists.
        *
        * Transitions the task's state to paused and calls its `on_pause` method
        * if the task is currently running.
        *
        * @param uid UID of the task to pause.
        *
        * @return `true` if the task was found and paused; otherwise `false`.
        */
        [[nodiscard]] status_code pause_task(task_uid_t uid);

        /**
        * @brief Resumes the specified task, if it exists and is paused.
        *
        * Transitions the task's state to resumed and calls its `on_resume` method
        * if the task was previously paused.
        *
        * @param uid UID of the task to resume.
        *
        * @return `true` if the task was found and resumed; otherwise `false`.
        */
        [[nodiscard]] status_code resume_task(task_uid_t uid);

        /**
        * @brief Aborts the specified task.
        *
        * Marks the task for termination, causing it to complete with an interrupted result.
        *
        * @param uid UID of the task to abort.
        *
        * @return `true` if the task was found and marked for abortion; otherwise `false`.
        */
        [[nodiscard]] status_code abort_task(task_uid_t uid);

        /**
        * @brief Executes an update cycle over all registered tasks.
        *
        * The `update` method:
        * - Processes all managed tasks.
        * - Calls appropriate lifecycle methods based on each task's state.
        * - Handles result dispatch via the associated channel.
        * - Cleans up completed or aborted tasks from the internal list.
        *
        * Should be called periodically in the main loop of the system.
        */
        void update();

    private:

        /**
        * @struct task_info
        * @brief Metadata bundle for a single managed task instance.
        *
        * This structure replaces the positional `std::tuple` with named fields to
        * improve readability and reduce bugs caused by index mix‑ups. It holds
        * everything the manager needs to drive a task through its lifecycle and
        * deliver results back to the originator.
        */
        struct task_info {
            /**
            * @brief Construct a fully-initialized record.
            * @param task_in        Owning handle to the task instance, obtained from `registry_t::emplace`.
            * @param state_in       Initial state (usually default-constructed).
            * @param initiator_id_in ID of the requester that initiated the task.
            * @param uid_in         Unique identifier of the task type.
            * @param channel_in     Channel used to deliver results back to the requester.
            *
            * @note `channel_in` is expected to be valid for the lifetime of this record.
            */
            task_info(
                typename registry_t::handle_t&& task_in,
                state state_in,
                uint8_t initiator_id_in,
                task_uid_t uid_in,
                channel_t* channel_in) noexcept;


            /**
            * @brief Owning handle to the managed task instance.
            *
            * The task object implements the lifecycle hooks (`on_start`, `on_execute`,
            * `on_complete`, `on_pause`, etc.) and exposes `is_finished()`. Ownership
            * *is* implied: dropping this handle (e.g. when the record is erased from
            * `_tasks`) destroys the task in its registry slot and frees the slot for
            * reuse. Losing track of a `task_info` without erasing it would leak the slot.
            */
            typename registry_t::handle_t task;

            /**
            * @brief Current runtime state flags of the task.
            *
            * Used by the manager to decide which lifecycle method to invoke next and
            * to coordinate transitions such as pause, resume, abort, and completion.
            */
            system::state state;

            /**
            * @brief Identifier of the component/device that initiated the task.
            *
            * Propagated back with the result so the recipient can correlate responses
            * on multi-tenant or multiplexed links.
            */
            uint8_t initiator_id;

            /**
            * @brief Unique identifier of the concrete task type.
            *
            * Serves as a compact, type-erased key for registry lookups and for routing
            * results through the communication layer.
            */
            task_uid_t uid;

            /**
            * @var channel
            * @brief Communication channel for delivering the task result.
            *
            * The manager calls `channel->on_result(initiator_id, uid, result, status)`
            * when a task completes or is aborted/interrupted.
            */
            channel_t* channel;
        };

        /**
        * @typedef tasks_container_t
        * @brief Internal storage for all currently registered tasks.
        *
        * Alias for the container that holds one @ref task_info record per managed task.
        *
        * @note Iterators and references to elements may be invalidated by operations
        *       that change the container size (e.g., `emplace_back`, `erase`, `clear`).
        * 
        * @todo Reimplement with a less saturated version of vector and preferably in 
        *       a preallocated storage.
        */
        using tasks_container_t = std::vector<task_info>;

        /**
        * @typedef task_iterator
        * @brief Mutable iterator over the task container.
        *
        * Iterator type produced by @ref tasks_container_t for traversing and
        * modifying @ref task_info entries in-place.
        */
        using task_iterator = typename tasks_container_t::iterator;

        /**
        * @brief Vector holding metadata and state for all currently registered tasks.
        */
        tasks_container_t _tasks;
        
        /**
        * @brief bitset tracking the completion status of each task in `_tasks`.
        *
        * Sized to `total_capacity` (concurrent task *slots*), not `sizeof...(Tasks)`
        * (task *types*): with any `capacity<Task, N>` tag where `N > 1`, more than
        * `sizeof...(Tasks)` instances can be concurrently alive in `_tasks`.
        */
        std::bitset<total_capacity> _garbage;

        /**
        * @brief Compile-time registry mapping task UIDs to constructors for creating task instances.
        *
        * @see registry_t
        */
        inline static registry_t _registry;

        /**
        * @brief Find the first task record with the specified UID.
        *
        * Performs a linear search over the internal task container to locate a
        * matching @ref task_info by its @ref task_info::uid field.
        *
        * @param uid Unique identifier of the concrete task type to search for.
        * @return Iterator to the matching record, or `_tasks.end()` if not found.
        *
        * @warning The returned iterator becomes invalid if `_tasks` is structurally
        *          modified (e.g., insertion or erasure). Do not cache it across calls
        *          that may mutate the container or after a call to `update()` that
        *          can erase completed/aborted tasks.
        */
        [[nodiscard]] task_iterator find(task_uid_t uid) noexcept;

        /**
        * @brief Reserved concurrent slot count for the task type identified by `raw_uid`.
        *
        * Folds over `Tasks...` at compile time, comparing each type's raw uid to
        * `raw_uid`; returns the matching type's `reg_t<T>::count` (1 for a bare
        * task type, `N` for a `capacity<Task, N>` tag). Used by `register_task`
        * to decide how many concurrent instances of a given uid may be alive
        * at once.
        *
        * @param raw_uid Raw uid to look up (as produced by `raw_uid_extractor`).
        * @return The reserved slot count, or `0` if `raw_uid` matches no registered task.
        */
        [[nodiscard]] static constexpr std::size_t capacity_of(raw_uid_t raw_uid) noexcept;

        /**
        * @brief Verifies that all tasks have a unique identified (`static constexpr [type] uid`).
        */
        static_assert((etools::meta::has_static_member_variable_uid_v<typename reg_t<Tasks>::type> && ...), "All tasks must have a static member 'uid' to uniquely identify them.");

        /**
        * @brief Ensures that all task types provided to the manager are distinct.
        *
        * Checked on the underlying task types (`reg_t<Tasks>::type`), not the
        * possibly-`capacity`-wrapped pack elements, so `Task` and `capacity<Task, N>`
        * are correctly recognised as the same task type for this purpose.
        */
        static_assert(etools::meta::is_distinct_v<typename reg_t<Tasks>::type...>, "All tasks types must be distinct.");

        /**
        * @brief Ensures that all task types can be constructed with a `etools::memory::buffer_view` parameter.
        *
        * @note This assumes every task has a single-`buffer_view` constructor. That
        *       premise is superseded by the native-typed-constructor/adapter design
        *       (schema-generated constructors take typed params, not a raw buffer_view)
        *       and this check will need to move to the adapter wiring once that lands.
        */
        static_assert((std::is_constructible_v<typename reg_t<Tasks>::type, etools::memory::buffer_view> && ...),
            "All tasks must have a constructor taking `etools::memory::buffer_view`");

        /**
        * @brief Ensures that all task types are derived from a comomn shared `task<uid_t>` base type.
        */
        static_assert((std::is_base_of_v<task_t, typename reg_t<Tasks>::type> && ...), "All task must derive from task<uid_t>");
    };
} // namespace etask::system

#include "task_manager.tpp"
#endif // ETASK_SYSTEM_TASK_MANAGER_HPP_