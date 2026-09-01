/**
* @file exercise.hpp
*
* @brief Starts one task by raw uid and reports which task actually ran.
*
* @note User-owned support code, not generated. It exists only for this
*       integration project.
*
* ## Why by raw uid, and not by name
*
* The obvious way to start a task is to name it:
* `config::internal.register_task(global::task_id::mesh_s0_n0_p0_sample)`. That
* would be worthless here. Naming the task in C++ means the compiler resolves
* the path, and a driver that named all 294 would be asserting that the
* *compiler* can tell them apart - which was never in question.
*
* What is in question is whether the **uids** tell them apart: whether the
* number in `.schema.uids.json` reaches the one task that owns it, through the
* registries the three managers build from the generated typelists. So this
* takes a `std::uint16_t` off the wire (or off stdin, on the host) and hands it
* to the manager as an opaque number, exactly as an arriving request would. The
* task that reports itself to the witness is then the answer, not the question.
*
* ## Why every task can be started the same way
*
* Each manager wraps its own tasks in `etask::core::task_unpack_adapter` /
* `scoped_task_unpack_adapter`, so every task in the project is constructible
* from one `etools::memory::buffer_view` of argument bytes regardless of what
* its native constructor takes. One zeroed payload therefore starts any of them;
* the arguments are never read, because no task in this tree does anything with
* them.
*/
#ifndef SUPPORT_EXERCISE_HPP_
#define SUPPORT_EXERCISE_HPP_
#include <cstdint>

namespace support {

    /**
    * @brief What starting one uid produced.
    */
    struct result {
        /// @brief The manager's `status_code`, as its underlying byte.
        std::uint8_t status;
        /// @brief How many witness entries the run produced. Expected to be 1.
        std::uint16_t reports;
        /// @brief The uid the task reported itself as; 0 if nothing reported.
        std::uint16_t reported_uid;
        /// @brief The `support::phase` of the report; 0 if nothing reported.
        std::uint8_t reported_phase;
    };

    /**
    * @brief Starts the task owning @p uid, runs it to completion, and reports.
    *
    * Clears the witness first, so what comes back describes this call alone.
    * Drives `config::manager.update()` a bounded number of times: every task in
    * this tree finishes on its first tick, so a run that needed more ticks than
    * that is a fault to surface rather than a loop to widen.
    *
    * An instant command never enters the manager at all - it runs inside
    * `register_task` - so for those the report is already in hand before the
    * first `update()`. Both paths are handled here rather than by the caller,
    * which does not know a uid's tier and should not have to.
    *
    * @param uid The raw task uid, as it would arrive in a request.
    * @return What ran, and what it said it was.
    */
    result exercise(std::uint16_t uid);

} // namespace support

#endif // SUPPORT_EXERCISE_HPP_
