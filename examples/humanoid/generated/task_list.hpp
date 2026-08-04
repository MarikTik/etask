// SPDX-License-Identifier: MIT
/**
* @file task_list.hpp
*
* @brief Every task type this application runs, as a typelist.
*
* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema
*          on every `etask-gen generate` run; hand edits are overwritten.
*          Build the task manager from it in your config, e.g.
*          `using manager_t = etask::core::task_manager_from_t<generated::task_list>;`.
*/
#ifndef GENERATED_TASK_LIST_HPP_
#define GENERATED_TASK_LIST_HPP_
#include <etools/meta/typelist.hpp>
#include <etools/factories/utils/capacity.hpp>
#include "../tasks/head/imu/read.hpp"
#include "../tasks/arms/left/move_to.hpp"
#include "../tasks/arms/left/stop.hpp"
#include "../tasks/arms/left/grasp.hpp"
#include "../tasks/arms/right/move_to.hpp"
#include "../tasks/arms/right/stop.hpp"
#include "../tasks/arms/right/grasp.hpp"
#include "../tasks/legs/left/step.hpp"
#include "../tasks/legs/left/stop.hpp"
#include "../tasks/legs/right/step.hpp"
#include "../tasks/legs/right/stop.hpp"
#include "../tasks/reboot.hpp"

namespace generated {

    using task_list = etools::meta::typelist<
        tasks::head::imu::read,
        etools::factories::utils::capacity<tasks::arms::left::move_to, 2>,
        tasks::arms::left::stop,
        tasks::arms::left::grasp,
        etools::factories::utils::capacity<tasks::arms::right::move_to, 2>,
        tasks::arms::right::stop,
        tasks::arms::right::grasp,
        tasks::legs::left::step,
        tasks::legs::left::stop,
        tasks::legs::right::step,
        tasks::legs::right::stop,
        tasks::reboot
    >;

} // namespace generated
#endif // GENERATED_TASK_LIST_HPP_
