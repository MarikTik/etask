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
#include "../sys/mesh/s0/n0/p0/sample.hpp"
#include "../sys/mesh/s0/n0/p0/arm.hpp"
#include "../sys/mesh/s0/n0/p0/hold.hpp"
#include "../sys/mesh/s0/n0/p0/quench.hpp"
#include "../sys/mesh/s0/n0/p1/sample.hpp"
#include "../sys/mesh/s0/n0/p1/arm.hpp"
#include "../sys/mesh/s0/n0/p1/hold.hpp"
#include "../sys/mesh/s0/n0/p1/quench.hpp"
#include "../sys/mesh/s0/n0/p2/sample.hpp"
#include "../sys/mesh/s0/n0/p2/arm.hpp"
#include "../sys/mesh/s0/n0/p2/hold.hpp"
#include "../sys/mesh/s0/n0/p2/quench.hpp"
#include "../sys/mesh/s0/n1/p0/sample.hpp"
#include "../sys/mesh/s0/n1/p0/arm.hpp"
#include "../sys/mesh/s0/n1/p0/hold.hpp"
#include "../sys/mesh/s0/n1/p0/quench.hpp"
#include "../sys/mesh/s0/n1/p1/sample.hpp"
#include "../sys/mesh/s0/n1/p1/arm.hpp"
#include "../sys/mesh/s0/n1/p1/hold.hpp"
#include "../sys/mesh/s0/n1/p1/quench.hpp"
#include "../sys/mesh/s0/n1/p2/sample.hpp"
#include "../sys/mesh/s0/n1/p2/arm.hpp"
#include "../sys/mesh/s0/n1/p2/hold.hpp"
#include "../sys/mesh/s0/n1/p2/quench.hpp"
#include "../sys/mesh/s0/n2/p0/sample.hpp"
#include "../sys/mesh/s0/n2/p0/arm.hpp"
#include "../sys/mesh/s0/n2/p0/hold.hpp"
#include "../sys/mesh/s0/n2/p0/quench.hpp"
#include "../sys/mesh/s0/n2/p1/sample.hpp"
#include "../sys/mesh/s0/n2/p1/arm.hpp"
#include "../sys/mesh/s0/n2/p1/hold.hpp"
#include "../sys/mesh/s0/n2/p1/quench.hpp"
#include "../sys/mesh/s0/n2/p2/sample.hpp"
#include "../sys/mesh/s0/n2/p2/arm.hpp"
#include "../sys/mesh/s0/n2/p2/hold.hpp"
#include "../sys/mesh/s0/n2/p2/quench.hpp"
#include "../sys/mesh/s0/n3/p0/sample.hpp"
#include "../sys/mesh/s0/n3/p0/arm.hpp"
#include "../sys/mesh/s0/n3/p0/hold.hpp"
#include "../sys/mesh/s0/n3/p0/quench.hpp"
#include "../sys/mesh/s0/n3/p1/sample.hpp"
#include "../sys/mesh/s0/n3/p1/arm.hpp"
#include "../sys/mesh/s0/n3/p1/hold.hpp"
#include "../sys/mesh/s0/n3/p1/quench.hpp"
#include "../sys/mesh/s0/n3/p2/sample.hpp"
#include "../sys/mesh/s0/n3/p2/arm.hpp"
#include "../sys/mesh/s0/n3/p2/hold.hpp"
#include "../sys/mesh/s0/n3/p2/quench.hpp"
#include "../sys/mesh/s1/n0/p0/sample.hpp"
#include "../sys/mesh/s1/n0/p0/arm.hpp"
#include "../sys/mesh/s1/n0/p0/hold.hpp"
#include "../sys/mesh/s1/n0/p0/quench.hpp"
#include "../sys/mesh/s1/n0/p1/sample.hpp"
#include "../sys/mesh/s1/n0/p1/arm.hpp"
#include "../sys/mesh/s1/n0/p1/hold.hpp"
#include "../sys/mesh/s1/n0/p1/quench.hpp"
#include "../sys/mesh/s1/n0/p2/sample.hpp"
#include "../sys/mesh/s1/n0/p2/arm.hpp"
#include "../sys/mesh/s1/n0/p2/hold.hpp"
#include "../sys/mesh/s1/n0/p2/quench.hpp"
#include "../sys/mesh/s1/n1/p0/sample.hpp"
#include "../sys/mesh/s1/n1/p0/arm.hpp"
#include "../sys/mesh/s1/n1/p0/hold.hpp"
#include "../sys/mesh/s1/n1/p0/quench.hpp"
#include "../sys/mesh/s1/n1/p1/sample.hpp"
#include "../sys/mesh/s1/n1/p1/arm.hpp"
#include "../sys/mesh/s1/n1/p1/hold.hpp"
#include "../sys/mesh/s1/n1/p1/quench.hpp"
#include "../sys/mesh/s1/n1/p2/sample.hpp"
#include "../sys/mesh/s1/n1/p2/arm.hpp"
#include "../sys/mesh/s1/n1/p2/hold.hpp"
#include "../sys/mesh/s1/n1/p2/quench.hpp"
#include "../sys/mesh/s1/n2/p0/sample.hpp"
#include "../sys/mesh/s1/n2/p0/arm.hpp"
#include "../sys/mesh/s1/n2/p0/hold.hpp"
#include "../sys/mesh/s1/n2/p0/quench.hpp"
#include "../sys/mesh/s1/n2/p1/sample.hpp"
#include "../sys/mesh/s1/n2/p1/arm.hpp"
#include "../sys/mesh/s1/n2/p1/hold.hpp"
#include "../sys/mesh/s1/n2/p1/quench.hpp"
#include "../sys/mesh/s1/n2/p2/sample.hpp"
#include "../sys/mesh/s1/n2/p2/arm.hpp"
#include "../sys/mesh/s1/n2/p2/hold.hpp"
#include "../sys/mesh/s1/n2/p2/quench.hpp"
#include "../sys/mesh/s1/n3/p0/sample.hpp"
#include "../sys/mesh/s1/n3/p0/arm.hpp"
#include "../sys/mesh/s1/n3/p0/hold.hpp"
#include "../sys/mesh/s1/n3/p0/quench.hpp"
#include "../sys/mesh/s1/n3/p1/sample.hpp"
#include "../sys/mesh/s1/n3/p1/arm.hpp"
#include "../sys/mesh/s1/n3/p1/hold.hpp"
#include "../sys/mesh/s1/n3/p1/quench.hpp"
#include "../sys/mesh/s1/n3/p2/sample.hpp"
#include "../sys/mesh/s1/n3/p2/arm.hpp"
#include "../sys/mesh/s1/n3/p2/hold.hpp"
#include "../sys/mesh/s1/n3/p2/quench.hpp"
#include "../sys/mesh/s2/n0/p0/sample.hpp"
#include "../sys/mesh/s2/n0/p0/arm.hpp"
#include "../sys/mesh/s2/n0/p0/hold.hpp"
#include "../sys/mesh/s2/n0/p0/quench.hpp"
#include "../sys/mesh/s2/n0/p1/sample.hpp"
#include "../sys/mesh/s2/n0/p1/arm.hpp"
#include "../sys/mesh/s2/n0/p1/hold.hpp"
#include "../sys/mesh/s2/n0/p1/quench.hpp"
#include "../sys/mesh/s2/n0/p2/sample.hpp"
#include "../sys/mesh/s2/n0/p2/arm.hpp"
#include "../sys/mesh/s2/n0/p2/hold.hpp"
#include "../sys/mesh/s2/n0/p2/quench.hpp"
#include "../sys/mesh/s2/n1/p0/sample.hpp"
#include "../sys/mesh/s2/n1/p0/arm.hpp"
#include "../sys/mesh/s2/n1/p0/hold.hpp"
#include "../sys/mesh/s2/n1/p0/quench.hpp"
#include "../sys/mesh/s2/n1/p1/sample.hpp"
#include "../sys/mesh/s2/n1/p1/arm.hpp"
#include "../sys/mesh/s2/n1/p1/hold.hpp"
#include "../sys/mesh/s2/n1/p1/quench.hpp"
#include "../sys/mesh/s2/n1/p2/sample.hpp"
#include "../sys/mesh/s2/n1/p2/arm.hpp"
#include "../sys/mesh/s2/n1/p2/hold.hpp"
#include "../sys/mesh/s2/n1/p2/quench.hpp"
#include "../sys/mesh/s2/n2/p0/sample.hpp"
#include "../sys/mesh/s2/n2/p0/arm.hpp"
#include "../sys/mesh/s2/n2/p0/hold.hpp"
#include "../sys/mesh/s2/n2/p0/quench.hpp"
#include "../sys/mesh/s2/n2/p1/sample.hpp"
#include "../sys/mesh/s2/n2/p1/arm.hpp"
#include "../sys/mesh/s2/n2/p1/hold.hpp"
#include "../sys/mesh/s2/n2/p1/quench.hpp"
#include "../sys/mesh/s2/n2/p2/sample.hpp"
#include "../sys/mesh/s2/n2/p2/arm.hpp"
#include "../sys/mesh/s2/n2/p2/hold.hpp"
#include "../sys/mesh/s2/n2/p2/quench.hpp"
#include "../sys/mesh/s2/n3/p0/sample.hpp"
#include "../sys/mesh/s2/n3/p0/arm.hpp"
#include "../sys/mesh/s2/n3/p0/hold.hpp"
#include "../sys/mesh/s2/n3/p0/quench.hpp"
#include "../sys/mesh/s2/n3/p1/sample.hpp"
#include "../sys/mesh/s2/n3/p1/arm.hpp"
#include "../sys/mesh/s2/n3/p1/hold.hpp"
#include "../sys/mesh/s2/n3/p1/quench.hpp"
#include "../sys/mesh/s2/n3/p2/sample.hpp"
#include "../sys/mesh/s2/n3/p2/arm.hpp"
#include "../sys/mesh/s2/n3/p2/hold.hpp"
#include "../sys/mesh/s2/n3/p2/quench.hpp"
#include "../sys/mesh/s3/n0/p0/sample.hpp"
#include "../sys/mesh/s3/n0/p0/arm.hpp"
#include "../sys/mesh/s3/n0/p0/hold.hpp"
#include "../sys/mesh/s3/n0/p0/quench.hpp"
#include "../sys/mesh/s3/n0/p1/sample.hpp"
#include "../sys/mesh/s3/n0/p1/arm.hpp"
#include "../sys/mesh/s3/n0/p1/hold.hpp"
#include "../sys/mesh/s3/n0/p1/quench.hpp"
#include "../sys/mesh/s3/n0/p2/sample.hpp"
#include "../sys/mesh/s3/n0/p2/arm.hpp"
#include "../sys/mesh/s3/n0/p2/hold.hpp"
#include "../sys/mesh/s3/n0/p2/quench.hpp"
#include "../sys/mesh/s3/n1/p0/sample.hpp"
#include "../sys/mesh/s3/n1/p0/arm.hpp"
#include "../sys/mesh/s3/n1/p0/hold.hpp"
#include "../sys/mesh/s3/n1/p0/quench.hpp"
#include "../sys/mesh/s3/n1/p1/sample.hpp"
#include "../sys/mesh/s3/n1/p1/arm.hpp"
#include "../sys/mesh/s3/n1/p1/hold.hpp"
#include "../sys/mesh/s3/n1/p1/quench.hpp"
#include "../sys/mesh/s3/n1/p2/sample.hpp"
#include "../sys/mesh/s3/n1/p2/arm.hpp"
#include "../sys/mesh/s3/n1/p2/hold.hpp"
#include "../sys/mesh/s3/n1/p2/quench.hpp"
#include "../sys/mesh/s3/n2/p0/sample.hpp"
#include "../sys/mesh/s3/n2/p0/arm.hpp"
#include "../sys/mesh/s3/n2/p0/hold.hpp"
#include "../sys/mesh/s3/n2/p0/quench.hpp"
#include "../sys/mesh/s3/n2/p1/sample.hpp"
#include "../sys/mesh/s3/n2/p1/arm.hpp"
#include "../sys/mesh/s3/n2/p1/hold.hpp"
#include "../sys/mesh/s3/n2/p1/quench.hpp"
#include "../sys/mesh/s3/n2/p2/sample.hpp"
#include "../sys/mesh/s3/n2/p2/arm.hpp"
#include "../sys/mesh/s3/n2/p2/hold.hpp"
#include "../sys/mesh/s3/n2/p2/quench.hpp"
#include "../sys/mesh/s3/n3/p0/sample.hpp"
#include "../sys/mesh/s3/n3/p0/arm.hpp"
#include "../sys/mesh/s3/n3/p0/hold.hpp"
#include "../sys/mesh/s3/n3/p0/quench.hpp"
#include "../sys/mesh/s3/n3/p1/sample.hpp"
#include "../sys/mesh/s3/n3/p1/arm.hpp"
#include "../sys/mesh/s3/n3/p1/hold.hpp"
#include "../sys/mesh/s3/n3/p1/quench.hpp"
#include "../sys/mesh/s3/n3/p2/sample.hpp"
#include "../sys/mesh/s3/n3/p2/arm.hpp"
#include "../sys/mesh/s3/n3/p2/hold.hpp"
#include "../sys/mesh/s3/n3/p2/quench.hpp"
#include "../sys/mesh/s4/n0/p0/sample.hpp"
#include "../sys/mesh/s4/n0/p0/arm.hpp"
#include "../sys/mesh/s4/n0/p0/hold.hpp"
#include "../sys/mesh/s4/n0/p0/quench.hpp"
#include "../sys/mesh/s4/n0/p1/sample.hpp"
#include "../sys/mesh/s4/n0/p1/arm.hpp"
#include "../sys/mesh/s4/n0/p1/hold.hpp"
#include "../sys/mesh/s4/n0/p1/quench.hpp"
#include "../sys/mesh/s4/n0/p2/sample.hpp"
#include "../sys/mesh/s4/n0/p2/arm.hpp"
#include "../sys/mesh/s4/n0/p2/hold.hpp"
#include "../sys/mesh/s4/n0/p2/quench.hpp"
#include "../sys/mesh/s4/n1/p0/sample.hpp"
#include "../sys/mesh/s4/n1/p0/arm.hpp"
#include "../sys/mesh/s4/n1/p0/hold.hpp"
#include "../sys/mesh/s4/n1/p0/quench.hpp"
#include "../sys/mesh/s4/n1/p1/sample.hpp"
#include "../sys/mesh/s4/n1/p1/arm.hpp"
#include "../sys/mesh/s4/n1/p1/hold.hpp"
#include "../sys/mesh/s4/n1/p1/quench.hpp"
#include "../sys/mesh/s4/n1/p2/sample.hpp"
#include "../sys/mesh/s4/n1/p2/arm.hpp"
#include "../sys/mesh/s4/n1/p2/hold.hpp"
#include "../sys/mesh/s4/n1/p2/quench.hpp"
#include "../sys/mesh/s4/n2/p0/sample.hpp"
#include "../sys/mesh/s4/n2/p0/arm.hpp"
#include "../sys/mesh/s4/n2/p0/hold.hpp"
#include "../sys/mesh/s4/n2/p0/quench.hpp"
#include "../sys/mesh/s4/n2/p1/sample.hpp"
#include "../sys/mesh/s4/n2/p1/arm.hpp"
#include "../sys/mesh/s4/n2/p1/hold.hpp"
#include "../sys/mesh/s4/n2/p1/quench.hpp"
#include "../sys/mesh/s4/n2/p2/sample.hpp"
#include "../sys/mesh/s4/n2/p2/arm.hpp"
#include "../sys/mesh/s4/n2/p2/hold.hpp"
#include "../sys/mesh/s4/n2/p2/quench.hpp"
#include "../sys/mesh/s4/n3/p0/sample.hpp"
#include "../sys/mesh/s4/n3/p0/arm.hpp"
#include "../sys/mesh/s4/n3/p0/hold.hpp"
#include "../sys/mesh/s4/n3/p0/quench.hpp"
#include "../sys/mesh/s4/n3/p1/sample.hpp"
#include "../sys/mesh/s4/n3/p1/arm.hpp"
#include "../sys/mesh/s4/n3/p1/hold.hpp"
#include "../sys/mesh/s4/n3/p1/quench.hpp"
#include "../sys/mesh/s4/n3/p2/sample.hpp"
#include "../sys/mesh/s4/n3/p2/arm.hpp"
#include "../sys/mesh/s4/n3/p2/hold.hpp"
#include "../sys/mesh/s4/n3/p2/quench.hpp"
#include "../sys/mesh/s5/n0/p0/sample.hpp"
#include "../sys/mesh/s5/n0/p0/arm.hpp"
#include "../sys/mesh/s5/n0/p0/hold.hpp"
#include "../sys/mesh/s5/n0/p0/quench.hpp"
#include "../sys/mesh/s5/n0/p1/sample.hpp"
#include "../sys/mesh/s5/n0/p1/arm.hpp"
#include "../sys/mesh/s5/n0/p1/hold.hpp"
#include "../sys/mesh/s5/n0/p1/quench.hpp"
#include "../sys/mesh/s5/n0/p2/sample.hpp"
#include "../sys/mesh/s5/n0/p2/arm.hpp"
#include "../sys/mesh/s5/n0/p2/hold.hpp"
#include "../sys/mesh/s5/n0/p2/quench.hpp"
#include "../sys/mesh/s5/n1/p0/sample.hpp"
#include "../sys/mesh/s5/n1/p0/arm.hpp"
#include "../sys/mesh/s5/n1/p0/hold.hpp"
#include "../sys/mesh/s5/n1/p0/quench.hpp"
#include "../sys/mesh/s5/n1/p1/sample.hpp"
#include "../sys/mesh/s5/n1/p1/arm.hpp"
#include "../sys/mesh/s5/n1/p1/hold.hpp"
#include "../sys/mesh/s5/n1/p1/quench.hpp"
#include "../sys/mesh/s5/n1/p2/sample.hpp"
#include "../sys/mesh/s5/n1/p2/arm.hpp"
#include "../sys/mesh/s5/n1/p2/hold.hpp"
#include "../sys/mesh/s5/n1/p2/quench.hpp"
#include "../sys/mesh/s5/n2/p0/sample.hpp"
#include "../sys/mesh/s5/n2/p0/arm.hpp"
#include "../sys/mesh/s5/n2/p0/hold.hpp"
#include "../sys/mesh/s5/n2/p0/quench.hpp"
#include "../sys/mesh/s5/n2/p1/sample.hpp"
#include "../sys/mesh/s5/n2/p1/arm.hpp"
#include "../sys/mesh/s5/n2/p1/hold.hpp"
#include "../sys/mesh/s5/n2/p1/quench.hpp"
#include "../sys/mesh/s5/n2/p2/sample.hpp"
#include "../sys/mesh/s5/n2/p2/arm.hpp"
#include "../sys/mesh/s5/n2/p2/hold.hpp"
#include "../sys/mesh/s5/n2/p2/quench.hpp"
#include "../sys/mesh/s5/n3/p0/sample.hpp"
#include "../sys/mesh/s5/n3/p0/arm.hpp"
#include "../sys/mesh/s5/n3/p0/hold.hpp"
#include "../sys/mesh/s5/n3/p0/quench.hpp"
#include "../sys/mesh/s5/n3/p1/sample.hpp"
#include "../sys/mesh/s5/n3/p1/arm.hpp"
#include "../sys/mesh/s5/n3/p1/hold.hpp"
#include "../sys/mesh/s5/n3/p1/quench.hpp"
#include "../sys/mesh/s5/n3/p2/sample.hpp"
#include "../sys/mesh/s5/n3/p2/arm.hpp"
#include "../sys/mesh/s5/n3/p2/hold.hpp"
#include "../sys/mesh/s5/n3/p2/quench.hpp"
#include "../sys/bus/link_state/probe.hpp"
#include "../sys/bus/link/state_probe2.hpp"
#include "../sys/bus/reserve/emergency_halt.hpp"
#include "../sys/bus/reserve/diagnostic.hpp"
#include "../sys/bus/reserve/audit.hpp"
#include "../sys/census.hpp"

namespace generated {

    /**
    * @brief Fire-and-forget commands (`instant_task`).
    *
    * Run to completion inside the call that delivers them: no storage, no
    * tick, no reply. Dispatched by `instant_task_manager`.
    */
    using instant_tasks = etools::meta::typelist<
        sys::mesh::s0::n0::p0::quench,
        sys::mesh::s0::n0::p1::quench,
        sys::mesh::s0::n0::p2::quench,
        sys::mesh::s0::n1::p0::quench,
        sys::mesh::s0::n1::p1::quench,
        sys::mesh::s0::n1::p2::quench,
        sys::mesh::s0::n2::p0::quench,
        sys::mesh::s0::n2::p1::quench,
        sys::mesh::s0::n2::p2::quench,
        sys::mesh::s0::n3::p0::quench,
        sys::mesh::s0::n3::p1::quench,
        sys::mesh::s0::n3::p2::quench,
        sys::mesh::s1::n0::p0::quench,
        sys::mesh::s1::n0::p1::quench,
        sys::mesh::s1::n0::p2::quench,
        sys::mesh::s1::n1::p0::quench,
        sys::mesh::s1::n1::p1::quench,
        sys::mesh::s1::n1::p2::quench,
        sys::mesh::s1::n2::p0::quench,
        sys::mesh::s1::n2::p1::quench,
        sys::mesh::s1::n2::p2::quench,
        sys::mesh::s1::n3::p0::quench,
        sys::mesh::s1::n3::p1::quench,
        sys::mesh::s1::n3::p2::quench,
        sys::mesh::s2::n0::p0::quench,
        sys::mesh::s2::n0::p1::quench,
        sys::mesh::s2::n0::p2::quench,
        sys::mesh::s2::n1::p0::quench,
        sys::mesh::s2::n1::p1::quench,
        sys::mesh::s2::n1::p2::quench,
        sys::mesh::s2::n2::p0::quench,
        sys::mesh::s2::n2::p1::quench,
        sys::mesh::s2::n2::p2::quench,
        sys::mesh::s2::n3::p0::quench,
        sys::mesh::s2::n3::p1::quench,
        sys::mesh::s2::n3::p2::quench,
        sys::mesh::s3::n0::p0::quench,
        sys::mesh::s3::n0::p1::quench,
        sys::mesh::s3::n0::p2::quench,
        sys::mesh::s3::n1::p0::quench,
        sys::mesh::s3::n1::p1::quench,
        sys::mesh::s3::n1::p2::quench,
        sys::mesh::s3::n2::p0::quench,
        sys::mesh::s3::n2::p1::quench,
        sys::mesh::s3::n2::p2::quench,
        sys::mesh::s3::n3::p0::quench,
        sys::mesh::s3::n3::p1::quench,
        sys::mesh::s3::n3::p2::quench,
        sys::mesh::s4::n0::p0::quench,
        sys::mesh::s4::n0::p1::quench,
        sys::mesh::s4::n0::p2::quench,
        sys::mesh::s4::n1::p0::quench,
        sys::mesh::s4::n1::p1::quench,
        sys::mesh::s4::n1::p2::quench,
        sys::mesh::s4::n2::p0::quench,
        sys::mesh::s4::n2::p1::quench,
        sys::mesh::s4::n2::p2::quench,
        sys::mesh::s4::n3::p0::quench,
        sys::mesh::s4::n3::p1::quench,
        sys::mesh::s4::n3::p2::quench,
        sys::mesh::s5::n0::p0::quench,
        sys::mesh::s5::n0::p1::quench,
        sys::mesh::s5::n0::p2::quench,
        sys::mesh::s5::n1::p0::quench,
        sys::mesh::s5::n1::p1::quench,
        sys::mesh::s5::n1::p2::quench,
        sys::mesh::s5::n2::p0::quench,
        sys::mesh::s5::n2::p1::quench,
        sys::mesh::s5::n2::p2::quench,
        sys::mesh::s5::n3::p0::quench,
        sys::mesh::s5::n3::p1::quench,
        sys::mesh::s5::n3::p2::quench,
        sys::bus::reserve::emergency_halt
    >;

    /**
    * @brief Tasks driven across ticks (`polled_task`, `oneshot_task`).
    *
    * Owned by `polled_task_manager`, which executes them until they report
    * themselves finished, then delivers the result. A `oneshot_task` belongs
    * here too - it is a polled task whose completion predicate is sealed.
    */
    using polled_tasks = etools::meta::typelist<
        sys::mesh::s0::n0::p0::sample,
        sys::mesh::s0::n0::p0::arm,
        sys::mesh::s0::n0::p1::sample,
        sys::mesh::s0::n0::p1::arm,
        sys::mesh::s0::n0::p2::sample,
        sys::mesh::s0::n0::p2::arm,
        sys::mesh::s0::n1::p0::sample,
        sys::mesh::s0::n1::p0::arm,
        sys::mesh::s0::n1::p1::sample,
        sys::mesh::s0::n1::p1::arm,
        sys::mesh::s0::n1::p2::sample,
        sys::mesh::s0::n1::p2::arm,
        sys::mesh::s0::n2::p0::sample,
        sys::mesh::s0::n2::p0::arm,
        sys::mesh::s0::n2::p1::sample,
        sys::mesh::s0::n2::p1::arm,
        sys::mesh::s0::n2::p2::sample,
        sys::mesh::s0::n2::p2::arm,
        sys::mesh::s0::n3::p0::sample,
        sys::mesh::s0::n3::p0::arm,
        sys::mesh::s0::n3::p1::sample,
        sys::mesh::s0::n3::p1::arm,
        sys::mesh::s0::n3::p2::sample,
        sys::mesh::s0::n3::p2::arm,
        sys::mesh::s1::n0::p0::sample,
        sys::mesh::s1::n0::p0::arm,
        sys::mesh::s1::n0::p1::sample,
        sys::mesh::s1::n0::p1::arm,
        sys::mesh::s1::n0::p2::sample,
        sys::mesh::s1::n0::p2::arm,
        sys::mesh::s1::n1::p0::sample,
        sys::mesh::s1::n1::p0::arm,
        sys::mesh::s1::n1::p1::sample,
        sys::mesh::s1::n1::p1::arm,
        sys::mesh::s1::n1::p2::sample,
        sys::mesh::s1::n1::p2::arm,
        sys::mesh::s1::n2::p0::sample,
        sys::mesh::s1::n2::p0::arm,
        sys::mesh::s1::n2::p1::sample,
        sys::mesh::s1::n2::p1::arm,
        sys::mesh::s1::n2::p2::sample,
        sys::mesh::s1::n2::p2::arm,
        sys::mesh::s1::n3::p0::sample,
        sys::mesh::s1::n3::p0::arm,
        sys::mesh::s1::n3::p1::sample,
        sys::mesh::s1::n3::p1::arm,
        sys::mesh::s1::n3::p2::sample,
        sys::mesh::s1::n3::p2::arm,
        sys::mesh::s2::n0::p0::sample,
        sys::mesh::s2::n0::p0::arm,
        sys::mesh::s2::n0::p1::sample,
        sys::mesh::s2::n0::p1::arm,
        sys::mesh::s2::n0::p2::sample,
        sys::mesh::s2::n0::p2::arm,
        sys::mesh::s2::n1::p0::sample,
        sys::mesh::s2::n1::p0::arm,
        sys::mesh::s2::n1::p1::sample,
        sys::mesh::s2::n1::p1::arm,
        sys::mesh::s2::n1::p2::sample,
        sys::mesh::s2::n1::p2::arm,
        sys::mesh::s2::n2::p0::sample,
        sys::mesh::s2::n2::p0::arm,
        sys::mesh::s2::n2::p1::sample,
        sys::mesh::s2::n2::p1::arm,
        sys::mesh::s2::n2::p2::sample,
        sys::mesh::s2::n2::p2::arm,
        sys::mesh::s2::n3::p0::sample,
        sys::mesh::s2::n3::p0::arm,
        sys::mesh::s2::n3::p1::sample,
        sys::mesh::s2::n3::p1::arm,
        sys::mesh::s2::n3::p2::sample,
        sys::mesh::s2::n3::p2::arm,
        sys::mesh::s3::n0::p0::sample,
        sys::mesh::s3::n0::p0::arm,
        sys::mesh::s3::n0::p1::sample,
        sys::mesh::s3::n0::p1::arm,
        sys::mesh::s3::n0::p2::sample,
        sys::mesh::s3::n0::p2::arm,
        sys::mesh::s3::n1::p0::sample,
        sys::mesh::s3::n1::p0::arm,
        sys::mesh::s3::n1::p1::sample,
        sys::mesh::s3::n1::p1::arm,
        sys::mesh::s3::n1::p2::sample,
        sys::mesh::s3::n1::p2::arm,
        sys::mesh::s3::n2::p0::sample,
        sys::mesh::s3::n2::p0::arm,
        sys::mesh::s3::n2::p1::sample,
        sys::mesh::s3::n2::p1::arm,
        sys::mesh::s3::n2::p2::sample,
        sys::mesh::s3::n2::p2::arm,
        sys::mesh::s3::n3::p0::sample,
        sys::mesh::s3::n3::p0::arm,
        sys::mesh::s3::n3::p1::sample,
        sys::mesh::s3::n3::p1::arm,
        sys::mesh::s3::n3::p2::sample,
        sys::mesh::s3::n3::p2::arm,
        sys::mesh::s4::n0::p0::sample,
        sys::mesh::s4::n0::p0::arm,
        sys::mesh::s4::n0::p1::sample,
        sys::mesh::s4::n0::p1::arm,
        sys::mesh::s4::n0::p2::sample,
        sys::mesh::s4::n0::p2::arm,
        sys::mesh::s4::n1::p0::sample,
        sys::mesh::s4::n1::p0::arm,
        sys::mesh::s4::n1::p1::sample,
        sys::mesh::s4::n1::p1::arm,
        sys::mesh::s4::n1::p2::sample,
        sys::mesh::s4::n1::p2::arm,
        sys::mesh::s4::n2::p0::sample,
        sys::mesh::s4::n2::p0::arm,
        sys::mesh::s4::n2::p1::sample,
        sys::mesh::s4::n2::p1::arm,
        sys::mesh::s4::n2::p2::sample,
        sys::mesh::s4::n2::p2::arm,
        sys::mesh::s4::n3::p0::sample,
        sys::mesh::s4::n3::p0::arm,
        sys::mesh::s4::n3::p1::sample,
        sys::mesh::s4::n3::p1::arm,
        sys::mesh::s4::n3::p2::sample,
        sys::mesh::s4::n3::p2::arm,
        sys::mesh::s5::n0::p0::sample,
        sys::mesh::s5::n0::p0::arm,
        sys::mesh::s5::n0::p1::sample,
        sys::mesh::s5::n0::p1::arm,
        sys::mesh::s5::n0::p2::sample,
        sys::mesh::s5::n0::p2::arm,
        sys::mesh::s5::n1::p0::sample,
        sys::mesh::s5::n1::p0::arm,
        sys::mesh::s5::n1::p1::sample,
        sys::mesh::s5::n1::p1::arm,
        sys::mesh::s5::n1::p2::sample,
        sys::mesh::s5::n1::p2::arm,
        sys::mesh::s5::n2::p0::sample,
        sys::mesh::s5::n2::p0::arm,
        sys::mesh::s5::n2::p1::sample,
        sys::mesh::s5::n2::p1::arm,
        sys::mesh::s5::n2::p2::sample,
        sys::mesh::s5::n2::p2::arm,
        sys::mesh::s5::n3::p0::sample,
        sys::mesh::s5::n3::p0::arm,
        sys::mesh::s5::n3::p1::sample,
        sys::mesh::s5::n3::p1::arm,
        sys::mesh::s5::n3::p2::sample,
        sys::mesh::s5::n3::p2::arm,
        sys::bus::link_state::probe,
        sys::bus::link::state_probe2,
        sys::bus::reserve::diagnostic,
        sys::bus::reserve::audit,
        sys::census
    >;

    /**
    * @brief How many polled tasks may be live at once.
    * Sizes the manager's inline record storage, so it is the tier's real
    *
    * Sizes the manager's inline record storage, so it is the tier's real
    * memory cost. One record per live task, held inline - no heap.
    *
    * Declared as `budget: polled:` in the schema. This tier's tasks reserve
    * 149 slots in total, so the declaration saves 141 records against that
    * worst case - on the project's word that no more than this many are ever
    * live at once.
    */
    inline constexpr std::size_t polled_budget = 8;

    /**
    * @brief Tasks that can be suspended (`stateful_task`).
    *
    * Owned by `stateful_task_manager`: everything the polled manager does,
    * plus honoring pause and resume.
    */
    using stateful_tasks = etools::meta::typelist<
        sys::mesh::s0::n0::p0::hold,
        sys::mesh::s0::n0::p1::hold,
        sys::mesh::s0::n0::p2::hold,
        sys::mesh::s0::n1::p0::hold,
        sys::mesh::s0::n1::p1::hold,
        sys::mesh::s0::n1::p2::hold,
        sys::mesh::s0::n2::p0::hold,
        sys::mesh::s0::n2::p1::hold,
        sys::mesh::s0::n2::p2::hold,
        sys::mesh::s0::n3::p0::hold,
        sys::mesh::s0::n3::p1::hold,
        sys::mesh::s0::n3::p2::hold,
        sys::mesh::s1::n0::p0::hold,
        sys::mesh::s1::n0::p1::hold,
        sys::mesh::s1::n0::p2::hold,
        sys::mesh::s1::n1::p0::hold,
        sys::mesh::s1::n1::p1::hold,
        sys::mesh::s1::n1::p2::hold,
        sys::mesh::s1::n2::p0::hold,
        sys::mesh::s1::n2::p1::hold,
        sys::mesh::s1::n2::p2::hold,
        sys::mesh::s1::n3::p0::hold,
        sys::mesh::s1::n3::p1::hold,
        sys::mesh::s1::n3::p2::hold,
        sys::mesh::s2::n0::p0::hold,
        sys::mesh::s2::n0::p1::hold,
        sys::mesh::s2::n0::p2::hold,
        sys::mesh::s2::n1::p0::hold,
        sys::mesh::s2::n1::p1::hold,
        sys::mesh::s2::n1::p2::hold,
        sys::mesh::s2::n2::p0::hold,
        sys::mesh::s2::n2::p1::hold,
        sys::mesh::s2::n2::p2::hold,
        sys::mesh::s2::n3::p0::hold,
        sys::mesh::s2::n3::p1::hold,
        sys::mesh::s2::n3::p2::hold,
        sys::mesh::s3::n0::p0::hold,
        sys::mesh::s3::n0::p1::hold,
        sys::mesh::s3::n0::p2::hold,
        sys::mesh::s3::n1::p0::hold,
        sys::mesh::s3::n1::p1::hold,
        sys::mesh::s3::n1::p2::hold,
        sys::mesh::s3::n2::p0::hold,
        sys::mesh::s3::n2::p1::hold,
        sys::mesh::s3::n2::p2::hold,
        sys::mesh::s3::n3::p0::hold,
        sys::mesh::s3::n3::p1::hold,
        sys::mesh::s3::n3::p2::hold,
        sys::mesh::s4::n0::p0::hold,
        sys::mesh::s4::n0::p1::hold,
        sys::mesh::s4::n0::p2::hold,
        sys::mesh::s4::n1::p0::hold,
        sys::mesh::s4::n1::p1::hold,
        sys::mesh::s4::n1::p2::hold,
        sys::mesh::s4::n2::p0::hold,
        sys::mesh::s4::n2::p1::hold,
        sys::mesh::s4::n2::p2::hold,
        sys::mesh::s4::n3::p0::hold,
        sys::mesh::s4::n3::p1::hold,
        sys::mesh::s4::n3::p2::hold,
        sys::mesh::s5::n0::p0::hold,
        sys::mesh::s5::n0::p1::hold,
        sys::mesh::s5::n0::p2::hold,
        sys::mesh::s5::n1::p0::hold,
        sys::mesh::s5::n1::p1::hold,
        sys::mesh::s5::n1::p2::hold,
        sys::mesh::s5::n2::p0::hold,
        sys::mesh::s5::n2::p1::hold,
        sys::mesh::s5::n2::p2::hold,
        sys::mesh::s5::n3::p0::hold,
        sys::mesh::s5::n3::p1::hold,
        sys::mesh::s5::n3::p2::hold
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
    * 72 slots in total, so the declaration saves 68 records against that
    * worst case - on the project's word that no more than this many are ever
    * live at once.
    */
    inline constexpr std::size_t stateful_budget = 4;

} // namespace generated
#endif // GENERATED_TASK_LIST_HPP_
