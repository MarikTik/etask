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
        nothing_acknowledge = 3,       ///< complete naturally, carrying no result
        nothing_report_status = 4,     ///< complete with a chosen status and no result
        scalars_unsigned_widths = 10,  ///< uint8/16/32/64 in one shape, ascending
        scalars_signed_widths = 9,     ///< int8/16/32/64, all negative
        scalars_plain_int = 6,         ///< the bare `int` alias, distinct from int32 in the schema
        scalars_reals = 8,             ///< float and double, at values that are not round
        scalars_flags = 5,             ///< bool, both ways
        scalars_positional = 7,        ///< the same values again, declared positionally
        wide_telemetry = 11,           ///< the project's widest result
        keyed_measure = 2,             ///< three branches, from eighteen bytes down to zero
        keyed_converge = 1,            ///< the aborted branch, reachable only by force-completing
        keyed_classify = 0,            ///< a custom status code keying its own shape
    };

} // namespace global
#endif // GLOBAL_TASK_ID_HPP_
