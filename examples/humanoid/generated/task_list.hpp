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
#include "../system/head/imu/read.hpp"
#include "../system/arms/left/move_to.hpp"
#include "../system/arms/left/stop.hpp"
#include "../system/arms/left/grasp.hpp"
#include "../system/arms/right/move_to.hpp"
#include "../system/arms/right/stop.hpp"
#include "../system/arms/right/grasp.hpp"
#include "../system/legs/left/step.hpp"
#include "../system/legs/left/stop.hpp"
#include "../system/legs/right/step.hpp"
#include "../system/legs/right/stop.hpp"
#include "../system/reboot.hpp"

namespace generated {

    using task_list = etools::meta::typelist<
        system::head::imu::read,
        etools::factories::utils::capacity<system::arms::left::move_to, 2>,
        system::arms::left::stop,
        system::arms::left::grasp,
        etools::factories::utils::capacity<system::arms::right::move_to, 2>,
        system::arms::right::stop,
        system::arms::right::grasp,
        system::legs::left::step,
        system::legs::left::stop,
        system::legs::right::step,
        system::legs::right::stop,
        system::reboot
    >;

} // namespace generated
#endif // GENERATED_TASK_LIST_HPP_
