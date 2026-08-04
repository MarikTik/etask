// SPDX-License-Identifier: MIT
/**
* @file task_id.hpp
*
* @brief Strongly-typed identifier for every task in the schema.
*
* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema
*          on every `etask-gen generate` run; hand edits are overwritten.
*          Each enumerator is named by the task's dotted schema path with
*          `.` replaced by `_`, and valued with the uid the generator
*          assigned (explicit in the schema, or path-hashed otherwise).
*/
#ifndef GLOBAL_TASK_ID_HPP_
#define GLOBAL_TASK_ID_HPP_
#include <cstdint>

namespace global {

    enum class task_id : std::uint8_t {
        rotors_fl_set_thrust = 139,       ///< drive this rotor to a thrust level
        rotors_fl_stop = 223,             ///< cut this rotor immediately
        rotors_fr_set_thrust = 35,        ///< drive this rotor to a thrust level
        rotors_fr_stop = 141,             ///< cut this rotor immediately
        rotors_rl_set_thrust = 51,        ///< drive this rotor to a thrust level
        rotors_rl_stop = 239,             ///< cut this rotor immediately
        rotors_rr_set_thrust = 42,        ///< drive this rotor to a thrust level
        rotors_rr_stop = 157,             ///< cut this rotor immediately
        sensors_imu_read = 84,            ///< sample accel + gyro
        sensors_baro_read_altitude = 18,  ///< read altitude above the launch point
        sensors_gps_fix = 29,             ///< acquire a position fix
        nav_fly_to = 16,                  ///< fly to a waypoint
        nav_hold = 243,                   ///< hold the current position
        nav_land = 41,                    ///< descend and touch down
        failsafe = 255,                   ///< emergency stop - cut every rotor now
    };

} // namespace global
#endif // GLOBAL_TASK_ID_HPP_
