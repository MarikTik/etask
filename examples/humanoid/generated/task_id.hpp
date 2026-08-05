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
        head_imu_read = 85,        ///< sample the accelerometer
        arms_left_move_to = 123,   ///< move the hand to a target pose
        arms_left_stop = 129,      ///< halt the arm immediately
        arms_left_grasp = 24,      ///< close the gripper until a force threshold
        arms_right_move_to = 102,  ///< move the hand to a target pose
        arms_right_stop = 151,     ///< halt the arm immediately
        arms_right_grasp = 86,     ///< close the gripper until a force threshold
        legs_left_step = 109,      ///< take one step
        legs_left_stop = 41,       ///< plant the foot and hold
        legs_right_step = 180,     ///< take one step
        legs_right_stop = 18,      ///< plant the foot and hold
        reboot = 255,              ///< reboot the controller
    };

} // namespace global
#endif // GLOBAL_TASK_ID_HPP_
