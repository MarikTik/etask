// SPDX-License-Identifier: BSL-1.1
/**
* @file simple_task2.hpp
*
* @note this is an example file, feel free to remove it in your project.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-08-14
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/

#ifndef TASKS_SIMPLE_TASK_2_HPP_
#define TASKS_SIMPLE_TASK_2_HPP_
#include "../task.hpp"

namespace tasks {
    class simple_task2 : public task {
    public:
        simple_task2(etools::memory::envelope_view env) noexcept;
        void on_start() override;

        static constexpr global::task_id uid = global::task_id::simple_task1; ///< Unique identifier for this task type
    };

} // namespace tasks
#endif // TASKS_SIMPLE_TASK_2_HPP_