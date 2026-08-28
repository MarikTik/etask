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
* The **task set** is generated - three typelists emitted from schema.yaml (see
* generated/task_list.hpp, rewritten every generate), one per task tier, because
* each tier is run by a different manager. The **manager instantiation** is
* yours: you build it from those lists with `task_manager_from_t`, so the task
* set never has to be hand-maintained here and regenerating it never rewrites
* this file.
*
* `generated/task_list.hpp` (and the `global::task_id` it references) do not
* exist until you run `cmake --build build --target etask-generate`. Generate
* first.
*/
#ifndef CONFIG_WIRING_HPP_
#define CONFIG_WIRING_HPP_
#include <etask/core/managers/managers.hpp>
#include <etask/core/channels/channels.hpp>
#include "protocol.hpp"
#include "generated/task_list.hpp"   // project root is on the include path (no `../`)

namespace config {

    /**
    * @brief The task manager type for this node: every task, routed by tier.
    *
    * The façade holds one sub-manager per tier and routes each uid to the one
    * that owns it - a compile-time decision. A tier with no tasks is an empty
    * typelist here, and nothing is instantiated for it: a project of pure
    * fire-and-forget commands carries no polling loop at all.
    *
    * @warning Generated tasks use native-typed constructors (e.g.
    *          `motor::spin(std::uint8_t duty, context&)`), which is the schema
    *          generator's design. The managed tiers currently expect each task to
    *          be constructible from a single `etools::memory::buffer_view`, so
    *          each must be wrapped in the payload-unpacking adapter
    *          (`task_unpack_adapter<Task, Args...>`, planned) - which the
    *          generated task lists will apply - before this compiles against
    *          native-ctor tasks. That adapter is the one remaining pipeline piece.
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
    //   inline etask::core::channels::external_channel<packet_t, support::channels::uart_channel, manager_t>
    //       external{link, manager};
    //
    // Then route inbound packets to it - see config/router.hpp - and poll the
    // router from app::loop(). `packet_t` comes from protocol.hpp.
    // -----------------------------------------------------------------------

} // namespace config

#endif // CONFIG_WIRING_HPP_
