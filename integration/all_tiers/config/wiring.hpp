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
#include "support/lifecycle/capturing_channel.hpp"

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

    /**
    * @brief The origin this project's scenarios actually register through.
    *
    * `internal` above is left in place because it is what a real node would use,
    * and because the manager is driven identically through either - but it
    * discards each result, and this project asserts on the results. See
    * support/lifecycle/capturing_channel.hpp for why that made a second channel
    * the smaller option than routing the lifecycle over a loopback link.
    *
    * Registering through a channel other than `internal` is not a special path:
    * `register_task` takes the origin as its first argument precisely so a node
    * can have several, and the manager treats them alike.
    */
    inline support::lifecycle::capturing_channel<manager_t> capture{};

    // -----------------------------------------------------------------------
    // External comms (optional). A node that only runs tasks it starts itself
    // needs none of this. To accept tasks over the wire, define a transport under
    // support/ (see support/README.md), instantiate it, and bind an
    // external_channel to it. Includes are top-level from the project root - no
    // `../` - and a subdirectory is a nested namespace:
    //
    //   #include "support/channels/uart_channel.hpp"
    //
    //   inline support::channels::uart_channel link{ your_port_handle };
    //
    //   inline etask::core::channels::external_channel<
    //       generated::links::<name>::request_packet_t,
    //       generated::links::<name>::reply_packet_t,
    //       support::channels::uart_channel, manager_t>
    //       external{link, manager};
    //
    // Then route inbound packets to it - see config/router.hpp - and poll the
    // router from app::loop(). The packet types come from generated/links.hpp,
    // sized from schema.yaml - declare the link there, not here.
    // -----------------------------------------------------------------------

} // namespace config

#endif // CONFIG_WIRING_HPP_
