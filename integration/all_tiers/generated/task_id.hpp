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
        instant_ping = 23,         ///< run on arrival and record it
        oneshot_sample = 122,      ///< one execution step, then answer
        polled_count_to = 71,      ///< execute for a fixed number of ticks, then finish
        polled_never_ends = 35,    ///< never finishes on its own; only a directive ends it
        stateful_resumable = 173,  ///< a long task that pauses and resumes safely
    };

} // namespace global
#endif // GLOBAL_TASK_ID_HPP_
