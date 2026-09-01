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
        swarm_salvo = 121,    ///< occupy a polled record for a fixed number of ticks
        swarm_volley = 158,   ///< occupy a polled record, but only two at a time
        swarm_single = 54,    ///< occupy a polled record, one instance only
        swarm_probe = 161,    ///< take a polled record for exactly one tick
        hold_latch = 85,      ///< hold a stateful record until told otherwise
        reset_counters = 53,  ///< zero the harness's bookkeeping, now
    };

} // namespace global
#endif // GLOBAL_TASK_ID_HPP_
