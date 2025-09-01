/**
* @file task.hpp
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef TASK_TASK_HPP_
#define TASK_TASK_HPP_
#include <etask/system/task.hpp>
#include <etools/memory/envelope_view.hpp>
#include "../global/task_id.hpp"
/**
* @brief Task type alias for the global task identifier.
* 
* This alias simplifies the usage of tasks throughout the application.
*/
using task = etask::system::task<global::task_id>;
#endif // TASK_TASK_HPP_