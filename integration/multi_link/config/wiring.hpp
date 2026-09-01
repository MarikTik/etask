/**
* @file wiring.hpp
*
* @brief The composition root: the task manager, and the channels bound to it.
*
* @note User-owned config. This is where the generated task set meets your
*       hand-written wiring. The task manager and channels are core library
*       templates (etask/core); nothing here is generated.
*
* ## What is generated vs. what is yours
*
* The **task set** is generated - three typelists emitted from schema.yaml, one
* per task tier, plus a budget for each managed tier (see
* generated/task_list.hpp, rewritten every generate). The **manager
* instantiation** is yours: you build it from those with `task_manager_from_t`,
* so the lists never have to be hand-maintained here and regenerating them
* never rewrites this file.
*
* `generated/task_list.hpp` (and the `global::task_id` it references) do not
* exist until you run `cmake --build build --target etask-generate`. Generate
* first.
*/
#ifndef CONFIG_WIRING_HPP_
#define CONFIG_WIRING_HPP_
#include <etask/core/managers/task_manager.hpp>
#include <etask/core/channels/channels.hpp>
#include "generated/links.hpp"   // packet types, sized from schema.yaml
#include "generated/task_list.hpp"   // project root is on the include path (no `../`)
#include "support/channels/stream_channel.hpp"

namespace config {

    /**
    * @brief The task manager type for this node: every task, routed by tier.
    *
    * The two budgets size each managed tier's inline record storage. As
    * generated they are the sum of that tier's per-task `concurrency` - every
    * task live at once, which is the most the schema alone can promise. That is
    * usually far more than a device really runs: measure your peak and set
    * `budget:` in the schema to reclaim the difference.
    *
    * @note Generated tasks use native-typed constructors (e.g.
    *       `motor::spin(std::uint8_t duty, context&)`), while a task arriving
    *       over the wire is an opaque payload. Each manager bridges that itself,
    *       wrapping its own tasks in `task_unpack_adapter` /
    *       `scoped_task_unpack_adapter` - so the generated lists name only task
    *       types, and nothing here has to mention the adapter.
    */
    using manager_t = etask::core::managers::task_manager_from_t<
        generated::instant_tasks,
        generated::polled_tasks,
        generated::stateful_tasks,
        generated::polled_budget,
        generated::stateful_budget>;

    /// @brief The one task manager instance.
    ///
    /// Holds its task records inline, sized by the budgets above - no heap, and
    /// no allocation at any point in a task's life.
    inline manager_t manager{};

    /// @brief Origin channel for tasks this node starts itself
    ///        (`config::internal.register_task(global::task_id::..., args...)`).
    inline etask::core::channels::internal_channel<manager_t> internal{manager};

    // -----------------------------------------------------------------------
    // External comms: two links, two channels, one manager.
    //
    // Both links reach the same task manager, and that is the arrangement under
    // test. Nothing about *which* tasks a wire may carry is decided here - it is
    // decided by each link's `subsystems:` in schema.yaml, projected into a
    // `carries()` the channel enforces. So this file names a policy nowhere; it
    // only pairs a link's traits with a transport.
    //
    // The traits struct is passed whole rather than as its constituent packet
    // types. That is the parameter that makes the pairing safe: with the two
    // packet types passed separately, `bench`'s frames and `net`'s allowlist
    // would compile happily together and the mistake would surface as a
    // correctly-checksummed frame carrying the wrong task.
    // -----------------------------------------------------------------------

    /**
    * @brief The `bench` link's transport - a raw serial pipe.
    *
    * Handed its descriptor by @ref app::setup, not opened here: which descriptor
    * this is differs between the board and the host test harness, and a
    * composition root that opened it would have to know which one it was
    * compiled for.
    */
    inline support::channels::stream_channel bench_transport{-1};

    /// @brief The `net` link's transport - a stream socket. @see bench_transport.
    inline support::channels::stream_channel net_transport{-1};

    /**
    * @brief The `bench` link: telemetry and shared, crc16, reliable.
    *
    * Sized for the narrow subsystems it carries. A request for `bulk.transfer`
    * arriving here is refused with `task_undefined_on_this_link` rather than
    * run - the task exists on this device, but not on this wire, and its
    * arguments would not fit these frames anyway.
    */
    inline etask::core::channels::external_channel<
        generated::links::bench::traits,
        support::channels::stream_channel,
        manager_t>
        bench{bench_transport, manager};

    /**
    * @brief The `net` link: bulk and shared, tcp, no checksum of our own.
    *
    * Carries the wide subsystem, so its frames are the larger pair. The
    * asymmetry with @ref bench is the whole point of declaring `subsystems:`:
    * one schema, two frame sizes, neither link paying for the other's traffic.
    */
    inline etask::core::channels::external_channel<
        generated::links::net::traits,
        support::channels::stream_channel,
        manager_t>
        net{net_transport, manager};

} // namespace config

#endif // CONFIG_WIRING_HPP_
