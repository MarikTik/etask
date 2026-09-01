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
#include <cstddef>
#include "../sys/bulk/transfer.hpp"
#include "../sys/telemetry/sample.hpp"
#include "../sys/shared/echo.hpp"
#include "../sys/ping.hpp"

namespace generated {

    /**
    * @brief Fire-and-forget commands (`instant_task`).
    *
    * Run to completion inside the call that delivers them: no storage, no
    * tick, no reply. Dispatched by `instant_task_manager`.
    *
    * This project declares none, so nothing is generated for this tier.
    */
    using instant_tasks = etools::meta::typelist<>;

    /**
    * @brief Tasks driven across ticks (`polled_task`, `oneshot_task`).
    *
    * Owned by `polled_task_manager`, which executes them until they report
    * themselves finished, then delivers the result. A `oneshot_task` belongs
    * here too - it is a polled task whose completion predicate is sealed.
    */
    using polled_tasks = etools::meta::typelist<
        sys::bulk::transfer,
        sys::telemetry::sample,
        sys::shared::echo,
        sys::ping
    >;

    /**
    * @brief How many polled tasks may be live at once.
    * Sizes the manager's inline record storage, so it is the tier's real
    *
    * Sizes the manager's inline record storage, so it is the tier's real
    * memory cost. One record per live task, held inline - no heap.
    *
    * Declared as `budget: polled:` in the schema. This tier's tasks reserve 4
    * slots in total, so the declaration saves 2 records against that worst
    * case - on the project's word that no more than this many are ever live
    * at once.
    */
    inline constexpr std::size_t polled_budget = 2;

    /**
    * @brief Tasks that can be suspended (`stateful_task`).
    *
    * Owned by `stateful_task_manager`: everything the polled manager does,
    * plus honoring pause and resume.
    *
    * This project declares none, so nothing is generated for this tier.
    */
    using stateful_tasks = etools::meta::typelist<>;

    /**
    * @brief How many stateful tasks may be live at once.
    * Sizes the manager's inline record storage, so it is the tier's real
    *
    * Sizes the manager's inline record storage, so it is the tier's real
    * memory cost. A suspended task still holds its record, so this tier fills
    * up on paused tasks as surely as on running ones.
    *
    * This is the sum of every task's `concurrency` in this tier - every task
    * running at its own limit simultaneously, which is the only bound the
    * schema alone implies. Most devices never approach it: measure your real
    * peak and set `budget:` in the schema to save the difference. The manager
    * rejects a budget above this sum, since the extra slots could never fill.
    */
    inline constexpr std::size_t stateful_budget = 0;

} // namespace generated
#endif // GENERATED_TASK_LIST_HPP_
