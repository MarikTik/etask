/**
* @file status_code.hpp
*
* @brief Defines the status codes used by the etask system for task execution reporting and error handling.
*
* @ingroup etask_system etask::system
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
#ifndef ETASK_SYSTEM_STATUS_CODE_HPP_
#define ETASK_SYSTEM_STATUS_CODE_HPP_
#include <cstdint>

namespace etask::system{
    /**
    * @enum status_code
    *
    * @brief Enumerates predefined status codes representing outcomes of task operations in the etask system.
    *
    * The `status_code` enumeration provides standardized result codes for task operations,
    * including success, various task lifecycle errors, and reserved values for user-defined
    * custom error codes. These codes are used across the etask framework to communicate
    * task states and execution results.
    *
    * @note
    * Custom user-defined error codes should start from the value defined in `custom_error_start`.
    */
    enum status_code : std::uint8_t {
        ok = 0,                      /**< General success code. */
        task_finished = 0,           /**< Indicates that a task completed successfully. */
        task_aborted = 1,            /**< The task was aborted before normal completion. */
        task_not_existing = 2,       /**< Referenced task does not exist in the system. */
        task_not_registered = 3,     /**< Attempt to operate on an unregistered task. */
        task_already_running = 4,    /**< The task is already in the running state. */
        task_already_paused = 5,     /**< The task is already paused. */
        task_already_resumed = 6,    /**< The task is already resumed. */
        custom_error_start = 55      /**< Start value for user-defined custom error codes. */
    };
} // namespace etask::system

#endif // ETASK_SYSTEM_STATUS_CODE_HPP_
 