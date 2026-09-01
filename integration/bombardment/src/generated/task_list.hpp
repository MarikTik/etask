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
#include "../sys/swarm/salvo.hpp"
#include "../sys/swarm/volley.hpp"
#include "../sys/swarm/single.hpp"
#include "../sys/swarm/probe.hpp"
#include "../sys/hold/latch.hpp"
#include "../sys/reset_counters.hpp"

namespace generated {

    /**
    * @brief Fire-and-forget commands (`instant_task`).
    *
    * Run to completion inside the call that delivers them: no storage, no
    * tick, no reply. Dispatched by `instant_task_manager`.
    */
    using instant_tasks = etools::meta::typelist<
        sys::reset_counters
    >;

    /**
    * @brief Tasks driven across ticks (`polled_task`, `oneshot_task`).
    *
    * Owned by `polled_task_manager`, which executes them until they report
    * themselves finished, then delivers the result. A `oneshot_task` belongs
    * here too - it is a polled task whose completion predicate is sealed.
    */
    using polled_tasks = etools::meta::typelist<
        etools::factories::utils::capacity<sys::swarm::salvo, 4>,
        etools::factories::utils::capacity<sys::swarm::volley, 2>,
        sys::swarm::single,
        etools::factories::utils::capacity<sys::swarm::probe, 2>
    >;

    /**
    * @brief How many polled tasks may be live at once.
    * Sizes the manager's inline record storage, so it is the tier's real
    *
    * Sizes the manager's inline record storage, so it is the tier's real
    * memory cost. One record per live task, held inline - no heap.
    *
    * Declared as `budget: polled:` in the schema. This tier's tasks reserve 9
    * slots in total, so the declaration saves 3 records against that worst
    * case - on the project's word that no more than this many are ever live
    * at once.
    */
    inline constexpr std::size_t polled_budget = 6;

    /**
    * @brief Tasks that can be suspended (`stateful_task`).
    *
    * Owned by `stateful_task_manager`: everything the polled manager does,
    * plus honoring pause and resume.
    */
    using stateful_tasks = etools::meta::typelist<
        etools::factories::utils::capacity<sys::hold::latch, 3>
    >;

    /**
    * @brief How many stateful tasks may be live at once.
    * Sizes the manager's inline record storage, so it is the tier's real
    *
    * Sizes the manager's inline record storage, so it is the tier's real
    * memory cost. A suspended task still holds its record, so this tier fills
    * up on paused tasks as surely as on running ones.
    *
    * Declared as `budget: stateful:` in the schema. This tier's tasks reserve
    * 3 slots in total, so the declaration saves 1 record against that worst
    * case - on the project's word that no more than this many are ever live
    * at once.
    */
    inline constexpr std::size_t stateful_budget = 2;

} // namespace generated
#endif // GENERATED_TASK_LIST_HPP_
