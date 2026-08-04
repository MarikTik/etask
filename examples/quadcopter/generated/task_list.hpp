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
#include "../system/rotors/fl/set_thrust.hpp"
#include "../system/rotors/fl/stop.hpp"
#include "../system/rotors/fr/set_thrust.hpp"
#include "../system/rotors/fr/stop.hpp"
#include "../system/rotors/rl/set_thrust.hpp"
#include "../system/rotors/rl/stop.hpp"
#include "../system/rotors/rr/set_thrust.hpp"
#include "../system/rotors/rr/stop.hpp"
#include "../system/sensors/imu/read.hpp"
#include "../system/sensors/baro/read_altitude.hpp"
#include "../system/sensors/gps/fix.hpp"
#include "../system/nav/fly_to.hpp"
#include "../system/nav/hold.hpp"
#include "../system/nav/land.hpp"
#include "../system/failsafe.hpp"

namespace generated {

    using task_list = etools::meta::typelist<
        etools::factories::utils::capacity<system::rotors::fl::set_thrust, 4>,
        system::rotors::fl::stop,
        etools::factories::utils::capacity<system::rotors::fr::set_thrust, 4>,
        system::rotors::fr::stop,
        etools::factories::utils::capacity<system::rotors::rl::set_thrust, 4>,
        system::rotors::rl::stop,
        etools::factories::utils::capacity<system::rotors::rr::set_thrust, 4>,
        system::rotors::rr::stop,
        system::sensors::imu::read,
        system::sensors::baro::read_altitude,
        system::sensors::gps::fix,
        system::nav::fly_to,
        system::nav::hold,
        system::nav::land,
        system::failsafe
    >;

} // namespace generated
#endif // GENERATED_TASK_LIST_HPP_
