/**
* @file task_manager.hpp 
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-03
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
#include "../tools/envelope.hpp"
#include "../internal/internal.hpp"
#include "../internal/meta.hpp"
#include "channel.hpp"
#include <tuple>
#include <array>
#include <vector>

create_has_member(uid) ///< Macro to create a type trait for task unique identifier (etask::intenral::has_member_uid).

namespace etask::system::management {

    /**
    * @class task_manager
    * @brief Manages the lifecycle and execution of tasks in the etask framework.
    *
    * The `task_manager` class provides methods to register, start, pause, resume,
    * and stop tasks. It orchestrates the execution flow and state transitions
    * of tasks, allowing for flexible task management in embedded systems.
    */
    template<typename ...Tasks>
    class task_manager {
    private:
        static_assert(internal::has_member_uid_v<Tasks...>, "All tasks must have a static member 'uid' to uniquely identify them.");
        static_assert(internal::is_distinct_v<Tasks...>, "All tasks types must be distinct.");

        /// @brief Type alias for task unique identifying obkecttype, derived from the Tasks parameter pack
        using task_uid_t = internal::template_parameter_of<Tasks...>;

        /// @brief Base task type for the task manager, derived from the Tasks parameter pack
        using task_t = tasks::task<task_uid_t>;

        /// @brief Underlying type for task identifiers, either enum or integral type
        using task_uuid_t = std::conditional_t<
            std::is_enum_v<task_uid_t>,
            std::underlying_type_t<task_uid_t>,
            task_uid_t
        >; 

        /// @brief Tuple type representing all required information about a registered task
        using task_info_t = std::tuple<
            task_t *, /// Pointer to the task instance
            tasks::state, /// Current state of the task
            channel & /// Communication channel reference for the task to send results
        >;
    public:
        task_manager(std::size_t max_task_load);
        void register_task(channel &origin, task_uid_t uid, tools::envelope params);
        void update();
    private:
        std::vector<task_info_t> _tasks;
        //std::array<task_info_t, sizeof...(Tasks)> _tasks; ///< Array of registerable tasks
    };



} // namespace etask::system::management

#endif // ETASK_SYSTEM_MANAGMENT_TASK_MANAGER_HPP_