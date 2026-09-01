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
#include "support/loopback_hub.hpp"  // this project's harness transport

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

    /**
    * @brief How many result bytes the internal channel's discard scratch holds.
    *
    * A task completed through `internal_channel` still runs `on_complete`, and
    * its `outcome` still packs somewhere - into a scratch buffer that is then
    * thrown away, since a locally-started task has no peer to answer. That
    * buffer's size is a template parameter with a **default of 64 bytes**, and
    * nothing derives it from the schema.
    *
    * That default is too small for this project. `wide.telemetry` returns 112
    * bytes; packed into a 64-byte scratch, `outcome` refuses the write and
    * reports `result_too_large` - a status the peer never sees here (nothing is
    * sent) but that a debug build asserts on, so the same schema that runs
    * correctly over the link aborts when the task is started locally.
    *
    * So it is spelled out, and derived from the one number the generator does
    * compute: the link's reply requirement, less the uid and status bytes it
    * includes. That keeps this in step with the schema automatically - widen a
    * return shape and this widens with it - rather than being a constant that
    * silently falls behind the next time a task grows.
    *
    * @note This is the workaround for a real gap, not a pattern to copy without
    *       reading it. `external_channel` static_asserts that its request packet
    *       can carry the widest parameter list, but there is no equivalent
    *       assertion on either the reply packet or this scratch, so an
    *       under-sized result region is a runtime surprise rather than a build
    *       failure. See this project's README.
    */
    inline constexpr std::size_t internal_scratch_bytes =
        generated::links::bench::reply_payload_need
        - sizeof(global::task_id) - sizeof(etask::core::status_code);

    /// @brief Origin channel for tasks this node starts itself
    ///        (`config::internal.register_task(global::task_id::..., args...)`).
    inline etask::core::channels::internal_channel<manager_t, internal_scratch_bytes>
        internal{manager};

    // -----------------------------------------------------------------------
    // External comms. This project accepts tasks over the `bench` link declared
    // in schema.yaml, because the reply direction is what it exists to test and
    // a reply has to have somewhere to go.
    //
    // The transport is an in-process hub rather than a serial port: what is under
    // test sits entirely above the transport, and every layer that does bear on
    // it - the channel, the reply protocol, the packet type generated from the
    // schema - is the real one. See support/loopback_hub.hpp for the full
    // argument. A board build swaps this one type for a real channel and changes
    // nothing else.
    // -----------------------------------------------------------------------

    /// @brief The `bench` link's transport: two queues the harness drives.
    using hub_t = support::loopback_hub<
        generated::links::bench::request_packet_t,
        generated::links::bench::reply_packet_t>;

    /// @brief The one hub instance; the harness pushes requests into it and reads
    ///        the reply frames back out.
    inline hub_t hub{};

    /**
    * @brief The channel bridging `bench` frames to the task manager.
    *
    * Instantiated on the link's `traits`, which carries both packet types, the
    * payload each direction must hold, the fingerprint and the uid allowlist -
    * so a channel cannot be built from one link's packets and another's rules.
    *
    * This link declares no `subsystems:`, so `carries()` is unconditionally true
    * and the handshake is bypassed: the fingerprint is `multi_link`'s subject,
    * and here it would only add a preamble exchange between the harness and
    * itself.
    */
    inline etask::core::channels::external_channel<
        generated::links::bench::traits, hub_t, manager_t>
        external{hub, manager};

} // namespace config

#endif // CONFIG_WIRING_HPP_
