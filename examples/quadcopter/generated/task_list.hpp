/**
* @file task_list.hpp
*
* @brief Every task type this application runs, split by tier.
*
* A task's tier decides which manager owns it, so the schema's tasks arrive
* here as three lists rather than one. A tier with no tasks is an empty
* typelist, and the façade instantiates nothing for it.
*
* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema
*          on every generate; hand edits are overwritten. Regenerate via the
*          CMake `etask-generate` target, or `etask generate`.
*          Build the task manager from these in your config:
*          `using manager_t = etask::core::managers::task_manager_from_t<`
*          `    generated::instant_tasks,`
*          `    generated::polled_tasks,`
*          `    generated::stateful_tasks>;`
*/
#ifndef GENERATED_TASK_LIST_HPP_
#define GENERATED_TASK_LIST_HPP_
#include <etools/meta/typelist.hpp>
#include <etools/factories/utils/capacity.hpp>
#include "../sys/rotors/fl/set_thrust.hpp"
#include "../sys/rotors/fl/stop.hpp"
#include "../sys/rotors/fr/set_thrust.hpp"
#include "../sys/rotors/fr/stop.hpp"
#include "../sys/rotors/rl/set_thrust.hpp"
#include "../sys/rotors/rl/stop.hpp"
#include "../sys/rotors/rr/set_thrust.hpp"
#include "../sys/rotors/rr/stop.hpp"
#include "../sys/sensors/imu/read.hpp"
#include "../sys/sensors/baro/read_altitude.hpp"
#include "../sys/sensors/gps/fix.hpp"
#include "../sys/nav/fly_to.hpp"
#include "../sys/nav/hold.hpp"
#include "../sys/nav/land.hpp"
#include "../sys/failsafe.hpp"

namespace generated {

    /**
    * @brief Fire-and-forget commands (`instant_task`).
    *
    * Run to completion inside the call that delivers them: no storage, no
    * tick, no reply. Dispatched by `instant_task_manager`.
    */
    using instant_tasks = etools::meta::typelist<
        sys::rotors::fl::stop,
        sys::rotors::fr::stop,
        sys::rotors::rl::stop,
        sys::rotors::rr::stop,
        sys::failsafe
    >;

    /**
    * @brief Tasks driven across ticks (`polled_task`, `oneshot_task`).
    *
    * Owned by `polled_task_manager`, which executes them until they report
    * themselves finished, then delivers the result. A `oneshot_task` belongs
    * here too - it is a polled task whose completion predicate is sealed.
    */
    using polled_tasks = etools::meta::typelist<
        etools::factories::utils::capacity<sys::rotors::fl::set_thrust, 4>,
        etools::factories::utils::capacity<sys::rotors::fr::set_thrust, 4>,
        etools::factories::utils::capacity<sys::rotors::rl::set_thrust, 4>,
        etools::factories::utils::capacity<sys::rotors::rr::set_thrust, 4>,
        sys::sensors::imu::read,
        sys::sensors::baro::read_altitude,
        sys::sensors::gps::fix,
        sys::nav::hold,
        sys::nav::land
    >;

    /**
    * @brief Tasks that can be suspended (`stateful_task`).
    *
    * Owned by `stateful_task_manager`: everything the polled manager does,
    * plus honoring pause and resume.
    */
    using stateful_tasks = etools::meta::typelist<
        sys::nav::fly_to
    >;

} // namespace generated
#endif // GENERATED_TASK_LIST_HPP_
