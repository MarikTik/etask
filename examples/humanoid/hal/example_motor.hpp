// SPDX-License-Identifier: MIT
/**
* @file example_motor.hpp
*
* @brief Example hardware driver - a stand-in for a real device (motor, sensor, ...).
*
* @note User-owned, and an EXAMPLE. `hal/` is where the hardware lives: the
*       drivers your tasks and contexts drive - motors, sensors, GPIO, ADCs. One
*       header per device (or a .hpp/.cpp pair for anything non-trivial). This
*       file shows the shape; adapt it, add siblings, or delete it. (Purely
*       software helpers - links, buffers, protocols - belong in support/ instead;
*       the split is a suggestion, not a rule.)
*
* ## How hardware reaches a task
*
* A driver defined here is owned by a *context*, not a task: put an instance in
* the user-owned area of the scope's generated context (sys/.../context.hpp):
*
*     // in sys/<scope>/context.hpp, in the "add your own state" area:
*     #include "../../hal/example_motor.hpp"
*     ...
*     struct context {
*         hal::example_motor motor;   // owned here, shared by the scope's tasks
*         ...
*     };
*
* Every task in that scope receives `context&` and drives `ctx.motor`. Hardware
* is constructed once, with the context, top-down - never inside a task.
*/
#ifndef HAL_EXAMPLE_MOTOR_HPP_
#define HAL_EXAMPLE_MOTOR_HPP_

namespace hal {

    /**
    * @brief Example device driver. Replace the bodies with real register/pin I/O.
    *
    * As written it does nothing (a no-op device), so the project builds before
    * any hardware exists; wire it to real peripherals when ready.
    */
    class example_motor {
    public:
        /// @brief Drive the motor to a normalized level in [0, 1]. TODO: implement.
        void set(float /*level*/) noexcept {
            // TODO: write to your PWM/DAC/register.
        }

        /// @brief Stop the motor immediately. TODO: implement.
        void stop() noexcept {
            // TODO: cut drive to the motor.
        }
    };

} // namespace hal

#endif // HAL_EXAMPLE_MOTOR_HPP_
