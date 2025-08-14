/**
* @file task_manager.hpp 
*
* @brief Declares the `task_manager` class for managing task lifecycles, state transitions, and result dispatch in the etask framework.
*
* @ingroup etask_system_management etask::system::management
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
* - @b Sticky @c resumed:
*   The `resumed` flag is an informational edge that stays set after a resume and is
*   typically cleared by a later pause. While running, `on_resume()` does not re-fire
*   because the manager gates it on `resumed && idle`.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-09
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_SYSTEM_MANAGMENT_TASK_MANAGER_HPP_
#define ETASK_SYSTEM_MANAGMENT_TASK_MANAGER_HPP_
#include "../tasks/tasks.hpp"
#include "../status_code.hpp"
#include "channel.hpp"
#include <tuple>
#include <vector>
#include <bitset>
#include <etools/meta/info_gen.hpp>
#include <etools/meta/traits.hpp>
#include <etools/meta/typelist.hpp>
#include <etools/memory/envelope_view.hpp>
#include <etools/facilities/registry.hpp>

generate_has_static_member_variable(uid) ///< Macro to create a type trait for task unique identifier cp check (etask::intenral::has_member_uid).

namespace etask::system::management {
    
    /**
    * @class task_manager
    *
    * @brief Manages the lifecycle, execution, and state transitions of tasks in the etask framework.
    *
    * The `task_manager` class provides a flexible, runtime mechanism for orchestrating task execution,
    * including registering new tasks, controlling their states, and dispatching results through
    * communication channels.
    *
    * Tasks managed by this class must:
    * - inherit from `etask::system::tasks::task`
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
    */
    template<typename Allocator, typename ...Tasks>
    class task_manager {
    private:

        /**
        * @struct uid_extractor
        *
        * @brief Metafunction for extracting the UID value from task types.
        *
        * Used by the `make_table` utility to generate the internal task type lookup table.
        */
        template<typename T> struct uid_extractor{ static constexpr auto value = T::uid; };

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
        * `task_uid_t` in the specialization of `tasks::task`.
        */
        using task_t = tasks::task<task_uid_t>;

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
    public:
        /**
        * @brief Constructs the task manager with an optional maximum task load.
        *
        * @param max_task_load Expected maximum number of tasks to be managed concurrently.
        *                      Used to preallocate storage for efficiency.
        * 
        * @warning The default number of concurrently running tasks is equal
        *          to the provided number of task types provided.
        *          It would be advised to specify a smaller load based on the 
        *          project requirements. For `sizeof...(Tasks)` <= 255, there 
        *          are no huge implications though.
        */
        task_manager(std::size_t max_task_load = sizeof...(Tasks));

        /**
        * @brief Registers a new task for execution.
        *
        * Searches for a matching task type in the internal table using the specified UID.
        * If found, instantiates the task and adds it to the list of managed tasks.
        *
        * @param origin Reference to the channel that will receive the task's result.
        * @param initiator_id ID of the device or component that initiated the task.
        * @param uid Unique identifier for the task type to instantiate.
        * @param params Envelope containing any parameters required by the task constructor.
        *
        * @return `true` if the task was successfully registered; otherwise `false`.
        */
        status_code register_task(channel_t *origin, uint8_t initiator_id, task_uid_t uid, etools::memory::envelope_view params);

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
        status_code pause_task(task_uid_t uid);

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
        status_code resume_task(task_uid_t uid);

        /**
        * @brief Aborts the specified task.
        *
        * Marks the task for termination, causing it to complete with an interrupted result.
        *
        * @param uid UID of the task to abort.
        *
        * @return `true` if the task was found and marked for abortion; otherwise `false`.
        */
        status_code abort_task(task_uid_t uid);

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
            * @param task_in        Pointer to the task instance owned/managed externally.
            * @param state_in       Initial state (usually default-constructed).
            * @param initiator_id_in ID of the requester that initiated the task.
            * @param uid_in         Unique identifier of the task type.
            * @param channel_in     Channel used to deliver results back to the requester.
            *
            * @note All pointers are expected to be valid for the lifetime of this record.
            */
            constexpr task_info(task_t* task_in,
                            tasks::state state_in,
                            uint8_t initiator_id_in,
                            task_uid_t uid_in,
                            channel_t* channel_in) noexcept;
            

            /**
            * @brief Pointer to the managed task instance.
            *
            * The task object implements the lifecycle hooks (`on_start`, `on_execute`,
            * `on_complete`, `on_pause`, etc.) and exposes `is_finished()`.
            * Ownership is not implied by this pointer unless stated elsewhere.
            */
            task_t* task;

            /**
            * @brief Current runtime state flags of the task.
            *
            * Used by the manager to decide which lifecycle method to invoke next and
            * to coordinate transitions such as pause, resume, abort, and completion.
            */
            tasks::state state;

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
        */
        std::bitset<sizeof...(Tasks)> _garbage;

        /**
        * @brief Compile-time table (std::array) mapping task UIDs to constructors for creating task instances.
        *
        * Generated at compile time using the `internal::make_table` mechanism.
        * Allows fast lookup of task constructors via binary search on UID values.
        */
        inline static auto &_registry = etools::facilities::registry<
            task_t,
            uid_extractor,
            etools::meta::typelist<Tasks...>,
            etools::meta::typelist<etools::memory::envelope_view>
        >::instance();

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
        task_iterator find(task_uid_t uid) noexcept;

        /**
        * @brief Verifies that all tasks have a unique identified (`static constexpr [type] uid`).
        */
        static_assert((etools::meta::has_static_member_variable_uid_v<Tasks> && ...), "All tasks must have a static member 'uid' to uniquely identify them.");

        /**
        * @brief Ensures that all task types provided to the manager are distinct.
        */
        static_assert(etools::meta::is_distinct_v<Tasks...>, "All tasks types must be distinct.");

        /**
        * @brief Ensures that all task types can be constructed with a `const tools::envelope&` parameter.
        */
        static_assert((std::is_constructible_v<Tasks, etools::memory::envelope_view> && ...), 
            "All tasks must have a constructor taking `etools::memory::envelope_view`");

        /**
        * @brief Ensures that all task types are derived from a comomn shared `task<uid_t>` base type.
        */
        static_assert((std::is_base_of_v<task_t, Tasks> && ...), "All task must derive from task<uid_t>");
    };
} // namespace etask::system::management

#include "task_manager.tpp"
#endif // ETASK_SYSTEM_MANAGMENT_TASK_MANAGER_HPP_