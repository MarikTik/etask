// SPDX-License-Identifier: BSL-1.1
/**
* @file simple_task1.hpp
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @note this is an example file, feel free to remove it in your project.
*
* @date 2025-08-14
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef TASKS_SIMPLE_TASK_1_HPP_
#define TASKS_SIMPLE_TASK_1_HPP_
#include "../task.hpp"

namespace tasks {
    class simple_task1 : public task {
    public:
        simple_task1(etools::memory::envelope_view env) noexcept;
        void on_start() override;

        static constexpr global::task_id uid = global::task_id::simple_task2; ///< Unique identifier for this task type
    };

} // namespace tasks
#endif // TASKS_SIMPLE_TASK_1_HPP_