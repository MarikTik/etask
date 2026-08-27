/**
* @file task_id.hpp
*
* @brief Strongly-typed identifier for every task in the schema.
*
* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema
*          on every generate; hand edits are overwritten. Regenerate via the
*          CMake `etask-generate` target, or `etask generate`.
*          Each enumerator is named by the task's dotted schema path with
*          `.` replaced by `_`, and valued with the uid the generator
*          assigned (explicit in the schema, or path-hashed otherwise).
*/
#ifndef GLOBAL_TASK_ID_HPP_
#define GLOBAL_TASK_ID_HPP_
#include <cstdint>

namespace global {

    enum class task_id : std::uint8_t {
        led_on = 61,               ///< drive the LED to a brightness, now
        led_off = 224,             ///< turn the LED off, now
        led_blink = 145,           ///< blink until it has blinked enough
        led_read_brightness = 92,  ///< report the current brightness
    };

} // namespace global
#endif // GLOBAL_TASK_ID_HPP_
