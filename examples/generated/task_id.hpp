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
        gripper_calibrate = 102,  ///< calibrate the gripper to a known zero
        gripper_grasp = 205,      ///< close the fingers until a force threshold is reached
        arm_base_move_to = 199,   ///< move the joint to an absolute angle
        arm_base_stop = 158,      ///< immediately halt the joint
        arm_elbow_move_to = 83,   ///< move the joint to an absolute angle
        arm_elbow_stop = 220,     ///< immediately halt the joint
        sensors_imu_read = 84,    ///< sample the accelerometer
        reboot = 255,             ///< reboot the controller
    };

} // namespace global
#endif // GLOBAL_TASK_ID_HPP_
