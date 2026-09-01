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
        bulk_transfer = 30,      ///< accept a wide payload and answer with a wide one
        telemetry_sample = 224,  ///< read one counter
        shared_echo = 75,        ///< return the argument, and which link asked
        ping = 245,              ///< a root-level task, belonging to no subsystem
    };

} // namespace global
#endif // GLOBAL_TASK_ID_HPP_
