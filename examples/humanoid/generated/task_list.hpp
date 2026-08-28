/**
* @file task_list.hpp
*
* @brief Every task type this application runs, split by tier.
*
* A task's tier decides which manager owns it, so the schema's tasks arrive
* here as three lists rather than one. A tier with no tasks is an empty
* typelist, and the façade instantiates nothing for it.
*
* Each managed tier also carries a budget: how many of its tasks may be live
* at once, which sizes that manager's inline storage.
*
* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema
*          on every generate; hand edits are overwritten. Regenerate via the
*          CMake `etask-generate` target, or `etask generate`.
*          Build the task manager from these in your config:
*          `using manager_t = etask::core::managers::task_manager_from_t<`
*          `    generated::instant_tasks,`
*          `    generated::polled_tasks,`
*          `    generated::stateful_tasks,`
*          `    generated::polled_budget,`
*          `    generated::stateful_budget>;`
*/
#ifndef GENERATED_TASK_LIST_HPP_
#define GENERATED_TASK_LIST_HPP_
#include <etools/meta/typelist.hpp>
#include <etools/factories/utils/capacity.hpp>
#include <cstddef>
#include "../sys/head/imu/read.hpp"
#include "../sys/arms/left/move_to.hpp"
#include "../sys/arms/left/stop.hpp"
#include "../sys/arms/left/grasp.hpp"
#include "../sys/arms/right/move_to.hpp"
#include "../sys/arms/right/stop.hpp"
#include "../sys/arms/right/grasp.hpp"
#include "../sys/legs/left/step.hpp"
#include "../sys/legs/left/stop.hpp"
#include "../sys/legs/right/step.hpp"
#include "../sys/legs/right/stop.hpp"
#include "../sys/reboot.hpp"

namespace generated {

    /**
    * @brief Fire-and-forget commands (`instant_task`).
    *
    * Run to completion inside the call that delivers them: no storage, no
    * tick, no reply. Dispatched by `instant_task_manager`.
    */
    using instant_tasks = etools::meta::typelist<
        sys::arms::left::stop,
        sys::arms::right::stop,
        sys::legs::left::stop,
        sys::legs::right::stop,
        sys::reboot
    >;

    /**
    * @brief Tasks driven across ticks (`polled_task`, `oneshot_task`).
    *
    * Owned by `polled_task_manager`, which executes them until they report
    * themselves finished, then delivers the result. A `oneshot_task` belongs
    * here too - it is a polled task whose completion predicate is sealed.
    */
    using polled_tasks = etools::meta::typelist<
        sys::head::imu::read,
        sys::arms::left::grasp,
        sys::arms::right::grasp,
        sys::legs::left::step,
        sys::legs::right::step
    >;

    /**
    * @brief How many polled tasks may be live at once.
    *
    * Sizes the manager's inline record storage, so it is the tier's real
    * memory cost. One record per live task, held inline - no heap.
    *
    * This is the sum of every task's `concurrency` in this tier - every task
    * running at its own limit simultaneously, which is the only bound the
    * schema alone implies. Most devices never approach it: measure your real
    * peak and set `budget:` in the schema to save the difference. The manager
    * rejects a budget above this sum, since the extra slots could never fill.
    */
    inline constexpr std::size_t polled_budget = 5;

    /**
    * @brief Tasks that can be suspended (`stateful_task`).
    *
    * Owned by `stateful_task_manager`: everything the polled manager does,
    * plus honoring pause and resume.
    */
    using stateful_tasks = etools::meta::typelist<
        etools::factories::utils::capacity<sys::arms::left::move_to, 2>,
        etools::factories::utils::capacity<sys::arms::right::move_to, 2>
    >;

    /**
    * @brief How many stateful tasks may be live at once.
    *
    * Sizes the manager's inline record storage, so it is the tier's real
    * memory cost. A suspended task still holds its record, so this tier fills up on paused tasks as surely as on running ones.
    *
    * This is the sum of every task's `concurrency` in this tier - every task
    * running at its own limit simultaneously, which is the only bound the
    * schema alone implies. Most devices never approach it: measure your real
    * peak and set `budget:` in the schema to save the difference. The manager
    * rejects a budget above this sum, since the extra slots could never fill.
    */
    inline constexpr std::size_t stateful_budget = 4;

} // namespace generated
#endif // GENERATED_TASK_LIST_HPP_
