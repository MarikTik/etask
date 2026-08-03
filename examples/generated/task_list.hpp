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
#include "../robot/gripper/calibrate.hpp"
#include "../robot/gripper/grasp.hpp"
#include "../robot/arm/base/move_to.hpp"
#include "../robot/arm/base/stop.hpp"
#include "../robot/arm/elbow/move_to.hpp"
#include "../robot/arm/elbow/stop.hpp"
#include "../robot/sensors/imu/read.hpp"
#include "../robot/reboot.hpp"

namespace generated {

    using task_list = etools::meta::typelist<
        tasks::gripper::calibrate,
        tasks::gripper::grasp,
        etools::factories::utils::capacity<tasks::arm::base::move_to, 2>,
        tasks::arm::base::stop,
        etools::factories::utils::capacity<tasks::arm::elbow::move_to, 2>,
        tasks::arm::elbow::stop,
        tasks::sensors::imu::read,
        tasks::reboot
    >;

} // namespace generated
#endif // GENERATED_TASK_LIST_HPP_
