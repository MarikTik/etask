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
#include "../sys/rotors/fl/set_thrust.hpp"
#include "../sys/rotors/fl/stop.hpp"
#include "../sys/rotors/fr/set_thrust.hpp"
#include "../sys/rotors/fr/stop.hpp"
#include "../sys/rotors/rl/set_thrust.hpp"
#include "../sys/rotors/rl/stop.hpp"
#include "../sys/rotors/rr/set_thrust.hpp"
#include "../sys/rotors/rr/stop.hpp"
#include "../sys/sensors/imu/read.hpp"
#include "../sys/sensors/baro/read_altitude.hpp"
#include "../sys/sensors/gps/fix.hpp"
#include "../sys/nav/fly_to.hpp"
#include "../sys/nav/hold.hpp"
#include "../sys/nav/land.hpp"
#include "../sys/failsafe.hpp"

namespace generated {

    using task_list = etools::meta::typelist<
        etools::factories::utils::capacity<sys::rotors::fl::set_thrust, 4>,
        sys::rotors::fl::stop,
        etools::factories::utils::capacity<sys::rotors::fr::set_thrust, 4>,
        sys::rotors::fr::stop,
        etools::factories::utils::capacity<sys::rotors::rl::set_thrust, 4>,
        sys::rotors::rl::stop,
        etools::factories::utils::capacity<sys::rotors::rr::set_thrust, 4>,
        sys::rotors::rr::stop,
        sys::sensors::imu::read,
        sys::sensors::baro::read_altitude,
        sys::sensors::gps::fix,
        sys::nav::fly_to,
        sys::nav::hold,
        sys::nav::land,
        sys::failsafe
    >;

} // namespace generated
#endif // GENERATED_TASK_LIST_HPP_
