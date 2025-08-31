// SPDX-License-Identifier: BSL-1.1
/**
* @file task_id.hpp
*
* @brief Global enumeration of user-defined task identifiers.
*
* This header centralizes the definition of task identifiers for the application.
* Each entry corresponds to a task type and must match the static `uid` declared
* in that task’s class. The task manager uses these identifiers to look up and
* construct tasks at runtime.
*
* @note This file is application-owned and is expected to be edited by the user.
*       Extend the enum as new tasks are introduced.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-08-10
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef GLOBAL_TASK_ID_HPP_
#define GLOBAL_TASK_ID_HPP_
#include <cstdint>

namespace global {

    /**
    * @enum task_id
    * @brief Strongly-typed enumeration of all task identifiers.
    *
    * Each enumerator uniquely identifies a task type and must match the `uid`
    * declared in the corresponding task class. This ensures correct registration
    * and dispatch through the task manager.
    *
    * @note The underlying type is `std::uint8_t`, allowing up to 256 distinct
    *       identifiers. For larger systems, this can be changed to `std::uint16_t`
    *       or a wider type, at the cost of increased memory footprint and protocol size.
    *
    * @warning Identifiers must remain unique across all tasks. Reuse or duplication
    *          will cause undefined behavior in the task manager.
    *
    * #### Example:
    * 
    * ```cpp
    * enum class task_id : std::uint8_t {
    *     network_scan,   ///< task for scanning network
    *     sensor_poll,    ///< task for polling sensors
    *     data_upload,    ///< task for uploading results
    * };
    * ```
    */
    enum class task_id : std::uint8_t {
        simple_task1, ///< Example identifier for task1
        simple_task2, ///< Example identifier for task2
    };

} // namespace global

#endif // GLOBAL_TASK_ID_HPP_
