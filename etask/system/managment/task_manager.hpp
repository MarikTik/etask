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
#include "../tools/tools.hpp"
#include "../internal/internal.hpp"
#include "channel.hpp"
#include <tuple>
#include <vector>
#include <bitset>

create_has_member(uid) ///< Macro to create a type trait for task unique identifier cp check (etask::intenral::has_member_uid).

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
    * ## Responsibilities
    * - Registering new task instances at runtime
    * - Maintaining task states (started, paused, resumed, aborted, finished)
    * - Calling appropriate lifecycle methods on tasks (start, execute, complete, pause, resume)
    * - Cleaning up completed or aborted tasks
    * - Forwarding task results through a `channel` abstraction
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
        using task_uid_t = internal::member_t<uid_extractor, Tasks...>;

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

        /**
        * @typedef task_info_t
        *
        * @brief Tuple containing all metadata required to manage a running task.
        *
        * The tuple elements include:
        * - Pointer to the task instance (`task_t*`)
        * - The current state of the task (`tasks::state`)
        * - The UID identifying the task type (`task_uid_t`)
        * - Reference to the channel used for delivering the task result (`channel&`)
        */
        using task_info_t = std::tuple<
            task_t *, /// Pointer to the task instance
            tasks::state, /// Current state of the task
            uint8_t, /// Initiator ID for the task (e.g., device that asked for the task to be executed)
            task_uid_t, /// Unique identifier for the task
            channel_t * /// Communication channel pointer for the task to send results
        >;
    public:
        /**
        * @brief Constructs the task manager with an optional maximum task load.
        *
        * @param max_task_load Expected maximum number of tasks to be managed concurrently.
        *                      Used to preallocate storage for efficiency.
        */
        task_manager(std::size_t max_task_load = sizeof...(Tasks));

        /**
        * @brief Registers a new task for execution.
        *
        * Searches for a matching task type in the internal table using the specified UID.
        * If found, instantiates the task and adds it to the list of managed tasks.
        *
        * @param origin Reference to the channel that will receive the task's result.
        * @param uid Unique identifier for the task type to instantiate.
        * @param params Envelope containing any parameters required by the task constructor.
        *
        * @return `true` if the task was successfully registered; otherwise `false`.
        */
        bool register_task(channel_t *origin, uint8_t initiator_id, task_uid_t uid, tools::envelope_view params);

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
        bool pause_task(task_uid_t uid);

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
        bool resume_task(task_uid_t uid);

        /**
        * @brief Aborts the specified task.
        *
        * Marks the task for termination, causing it to complete with an interrupted result.
        *
        * @param uid UID of the task to abort.
        *
        * @return `true` if the task was found and marked for abortion; otherwise `false`.
        */
        bool abort_task(task_uid_t uid);

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
        * @brief Vector holding metadata and state for all currently registered tasks.
        */
        std::vector<task_info_t> _tasks;
        
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
        inline static auto _task_table = internal::identity_table_gen<
            task_t,
            uid_extractor,
            Allocator,
            internal::typelist<Tasks...>,
            internal::typelist<tools::envelope_view>
        >::value;

        /**
        * @brief Load factor used to reserve memory in the task vector to improve performance.
        */
        static constexpr float _load_factor = 0.75f;


        /**
        * @brief Verifies that all tasks have a unique identified (`static constexpr [type] uid`).
        */
        static_assert((internal::has_member_uid_v<Tasks> && ...), "All tasks must have a static member 'uid' to uniquely identify them.");

        /**
        * @brief Ensures that all task types provided to the manager are distinct.
        */
        static_assert(internal::is_distinct_v<Tasks...>, "All tasks types must be distinct.");

        /**
        * @brief Ensures that all task types can be constructed with a `const tools::envelope&` parameter.
        */
        static_assert((std::is_constructible_v<Tasks, const tools::envelope&> && ...), "All tasks must have a constructor taking const tools::envelope&");
    };

} // namespace etask::system::management

#include "task_manager.tpp"
#endif // ETASK_SYSTEM_MANAGMENT_TASK_MANAGER_HPP_