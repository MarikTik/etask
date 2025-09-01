// SPDX-License-Identifier: BSL-1.1
/**
* @file simple_task1.cpp
*
* @brief Definition of simple_task1.hpp api.
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
#include "simple_task1.hpp"

namespace tasks {
    simple_task1::simple_task1([[maybe_unused]] etools::memory::envelope_view env) noexcept
    {
        // discard env since no parameter are expected by the task
    }
    void simple_task1::on_start()
    {
        // Initialization logic can be added here if needed
    }
}