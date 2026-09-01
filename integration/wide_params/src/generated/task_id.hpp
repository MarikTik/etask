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
        echo_echo_bool = 0,      ///< echo a bool
        echo_echo_int8 = 7,      ///< echo an int8
        echo_echo_uint8 = 11,    ///< echo a uint8
        echo_echo_int16 = 4,     ///< echo an int16
        echo_echo_uint16 = 8,    ///< echo a uint16
        echo_echo_int32 = 5,     ///< echo an int32
        echo_echo_uint32 = 9,    ///< echo a uint32
        echo_echo_int64 = 6,     ///< echo an int64
        echo_echo_uint64 = 10,   ///< echo a uint64
        echo_echo_float = 2,     ///< echo a float
        echo_echo_double = 1,    ///< echo a double
        echo_echo_int = 3,       ///< echo an `int` (the schema's alias for int32)
        mixed_sandwich = 14,     ///< uint8, double, uint8 - the canonical padding trap
        mixed_staircase = 16,    ///< widths ascending 1,2,4,8 - every field naturally aligned
        mixed_avalanche = 12,    ///< widths descending 8,4,2,1 then ascending again
        mixed_odd_pair = 13,     ///< bool, double, bool, float - the two floating widths off-alignment
        mixed_signed_run = 15,   ///< alternating signed and unsigned at every width
        wide_everything = 17,    ///< every scalar type once, in one call
        wide_saturated = 19,     ///< six doubles - the widest single-type list, folded on return
        wide_folded_mixed = 18,  ///< a wide mixed list, folded over the raw argument bytes
    };

} // namespace global
#endif // GLOBAL_TASK_ID_HPP_
