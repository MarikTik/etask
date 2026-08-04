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
#include "../sys/head/imu/read.hpp"
#include "../sys/arms/left/move_to.hpp"
#include "../sys/arms/left/stop.hpp"
#include "../sys/arms/left/grasp.hpp"
#include "../sys/arms/right/move_to.hpp"
#include "../sys/arms/right/stop.hpp"
#include "../sys/arms/right/grasp.hpp"
#include "../sys/legs/left/step.hpp"
#include "../sys/legs/left/stop.hpp"
#include "../sys/legs/right/step.hpp"
#include "../sys/legs/right/stop.hpp"
#include "../sys/reboot.hpp"

namespace generated {

    using task_list = etools::meta::typelist<
        sys::head::imu::read,
        etools::factories::utils::capacity<sys::arms::left::move_to, 2>,
        sys::arms::left::stop,
        sys::arms::left::grasp,
        etools::factories::utils::capacity<sys::arms::right::move_to, 2>,
        sys::arms::right::stop,
        sys::arms::right::grasp,
        sys::legs::left::step,
        sys::legs::left::stop,
        sys::legs::right::step,
        sys::legs::right::stop,
        sys::reboot
    >;

} // namespace generated
#endif // GENERATED_TASK_LIST_HPP_
