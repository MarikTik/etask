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
    // External comms: NOT WIRED, and not by choice. Read this before adding it.
    //
    // This project needs the link more than most - verify.py drives the device
    // over it, and without it the ESP32 build proves only that the tasks
    // compile for Xtensa, not that their bytes survive the trip. It is left out
    // because the two halves of the framework do not currently meet here.
    //
    // `etask::core::channels::external_channel` takes one `Link` traits type
    // and reads four things off it:
    //
    //   Link::request_packet_t      Link::request_payload_need
    //   Link::reply_packet_t        Link::fingerprint
    //                               Link::carries(uid)
    //
    // `generated/links.hpp` emits the first three as loose constants inside a
    // *namespace* `generated::links::bench`, and emits neither `fingerprint`
    // nor `carries`. A namespace cannot be a template argument, so there is no
    // spelling of this instantiation that compiles - the generator and the
    // runtime are a revision apart on what a "link" is.
    //
    // The gap is the generator's: the runtime's shape is the newer and the
    // better one (one type per link, so a call site cannot pair one link's
    // packets with another's uid set). `links_file.py` needs to emit a
    // `struct traits` per link carrying those five members. Until it does,
    // hand-writing the struct here would mean hand-maintaining a copy of the
    // sizes the schema exists to compute, in the one project whose whole
    // subject is those sizes being right.
    //
    // Once the generator emits it, this becomes:
    //
    //   #include <ecomm/channels/arduino_serial_channel.hpp>
    //
    //   inline ecomm::channels::arduino_serial_channel<0> link{Serial};
    //
    //   inline etask::core::channels::external_channel<
    //       generated::links::bench::traits, decltype(link), manager_t>
    //       external{link, manager};
    //
    // Then route inbound packets to it - see config/router.hpp - and poll the
    // router from app::loop(). The packet types come from generated/links.hpp,
    // sized from schema.yaml - declare the link there, not here.
    // -----------------------------------------------------------------------

} // namespace config

#endif // CONFIG_WIRING_HPP_
