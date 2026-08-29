from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Tuple


@dataclass
class ScaffoldReport:
    """What the scaffolder did, for CLI reporting and tests."""

    created: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


class Scaffold:
    """Lays down the *non-generated* half of an etask project - the integration
    layer the code generator can never write for you.

    Where :class:`Emitter` owns ``sys/`` (the task tree, contexts, ``task.hpp``)
    and ``generated/`` (the enum + typelist), this owns everything around them:
    the entry point, the app lifecycle, the wiring that turns the generated task
    set into a live ``task_manager``, the wire protocol, and example transport /
    hardware drivers. Together the two halves are a project you can read
    end-to-end and build.

    Every file here is **created once, then yours**. Re-running the scaffold on an
    existing project skips any file that already exists - it never clobbers your
    edits (that is what "append it wisely" means: fill the gaps, touch nothing
    that is already there).

    ## The layout it writes

    ```
    <project>/
      CMakeLists.txt   main.cpp   app.hpp   app.cpp   ← root: the app, acting on all parts (namespace app)
      schema.yaml                                       ← the generator's input (seed; kept if present)
      config/  wiring.hpp  router.hpp                   ← bridging (namespace config)
      hal/     example_motor.hpp                         ← hardware drivers a context owns (namespace hal)
      support/ example_channel.hpp                       ← software / linking helpers, incl. transport (namespace support)
    ```

    ``sys/`` and ``generated/`` are produced by ``etask generate`` and are not
    written here.
    """

    @staticmethod
    def files() -> List[Tuple[str, Callable[[], str]]]:
        """(relative path, renderer) for every scaffold file, in write order."""
        return [
            ("CMakeLists.txt", Scaffold.__cmake),
            ("main.cpp", Scaffold.__main_cpp),
            ("app.hpp", Scaffold.__app_hpp),
            ("app.cpp", Scaffold.__app_cpp),
            ("schema.yaml", Scaffold.__schema_yaml),
            ("config/wiring.hpp", Scaffold.__wiring_hpp),
            ("config/router.hpp", Scaffold.__router_hpp),
            ("hal/README.md", Scaffold.__hal_readme),
            ("support/README.md", Scaffold.__support_readme),
        ]

    @staticmethod
    def write(target: Path) -> ScaffoldReport:
        """Write the scaffold into ``target``, skipping files that already exist."""
        report = ScaffoldReport()
        for rel, render in Scaffold.files():
            path = target / rel
            if path.exists():
                report.skipped.append(str(path))
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(render())
            report.created.append(str(path))
        return report

    # =====================================================================
    # Root: entry point + app lifecycle (namespace app)
    # =====================================================================

    @staticmethod
    def __cmake() -> str:
        return '''\
#
# Starter CMake for an etask application. This is the *scaffolded* (non-generated)
# half of the project; the generated half - the sys/ task tree and generated/
# (task_id enum + task_list typelist) - comes from `etask generate` on schema.yaml.
cmake_minimum_required(VERSION 3.20)
project(etask_app LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ---------------------------------------------------------------------------------------
# This node's identity on the wire (1..254), used when it initiates tasks itself.
# ---------------------------------------------------------------------------------------
set(ECOMM_BOARD_ID 1 CACHE STRING "This device's ecomm node id (1..254)")

# ---------------------------------------------------------------------------------------
# The etask framework. It transitively brings ecomm + etools, and its repository
# also carries the schema code generator used by the `etask-generate` target below.
# ---------------------------------------------------------------------------------------
include(FetchContent)
FetchContent_Declare(
  etask
  GIT_REPOSITORY https://github.com/MarikTik/etask.git
  GIT_TAG        main   # pin to a release tag for reproducible builds
)
FetchContent_MakeAvailable(etask)

# ---------------------------------------------------------------------------------------
# Code generation: schema.yaml -> sys/ scaffolds (once) + generated/ (always).
#
#   cmake --build build --target etask-generate
#
# Run this after editing schema.yaml, then re-configure so CMake picks up any
# newly generated sys/**/*.cpp task bodies (globbed at configure time).
# ---------------------------------------------------------------------------------------
find_package(Python3 COMPONENTS Interpreter REQUIRED)

add_custom_target(etask-generate
  COMMAND ${CMAKE_COMMAND} -E env
          PYTHONPATH=${etask_SOURCE_DIR}/tools/src
          ${Python3_EXECUTABLE} -m etask.schema.cli generate
          ${CMAKE_CURRENT_SOURCE_DIR}/schema.yaml
          --out        ${CMAKE_CURRENT_SOURCE_DIR}/sys
          --task-id    ${CMAKE_CURRENT_SOURCE_DIR}/generated/task_id.hpp
          --task-list  ${CMAKE_CURRENT_SOURCE_DIR}/generated/task_list.hpp
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  COMMENT "etask: generating sys/ scaffolds and generated/ (task_id, task_list) from schema.yaml"
  VERBATIM
)

# ---------------------------------------------------------------------------------------
# The application: the root entry point + lifecycle (main.cpp, app.cpp), the
# generated task bodies under sys/, and any .cpp you add under hal/ or support/.
# (Re-run CMake configure after adding files so the globs pick them up.)
# ---------------------------------------------------------------------------------------
file(GLOB_RECURSE APP_TASK_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/sys/*.cpp")
file(GLOB_RECURSE APP_LIB_SOURCES  CONFIGURE_DEPENDS
     "${CMAKE_CURRENT_SOURCE_DIR}/hal/*.cpp"
     "${CMAKE_CURRENT_SOURCE_DIR}/support/*.cpp")

add_executable(app main.cpp app.cpp ${APP_TASK_SOURCES} ${APP_LIB_SOURCES})

# The project root is the sole include root: every top-level directory is then
# reachable by its own path from ANY file at ANY depth - `#include "hal/imu/x.hpp"`,
# `#include "support/channels/y.hpp"`, `#include "generated/links.hpp"` - with no
# `../` walks. Add the root, not each subdir, so the top-level prefix is required
# (and never ambiguous).
target_include_directories(app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(app PRIVATE etask)
target_compile_definitions(app PRIVATE ECOMM_BOARD_ID=${ECOMM_BOARD_ID})
'''

    @staticmethod
    def __main_cpp() -> str:
        return '''\
/**
* @file main.cpp
*
* @brief Plain-`main` entry point: drives the application's lifecycle.
*
* @note User-owned, and intentionally trivial. The application logic lives in
*       `app::setup()` / `app::loop()` (see app.hpp), so this file is just the
*       adapter between your platform's entry point and the app.
*
*       On an Arduino core you would not use this file at all - instead the
*       sketch forwards the program-level hooks:
*       ```cpp
*       void setup() { app::setup(); }
*       void loop()  { app::loop(); }
*       ```
*/
#include "app.hpp"

int main() {
    app::setup();
    while (true) app::loop();
    return 0;
}
'''

    @staticmethod
    def __app_hpp() -> str:
        return '''\
/**
* @file app.hpp
*
* @brief The application's two lifecycle entry points: `setup` and `loop`.
*
* @note User-owned, and the top of the project. `app` is where all the parts are
*       actually acted upon - it draws on `config::` (the wiring and settings) to
*       bring the node to life. It lives at the project root, next to main.cpp,
*       precisely because it is not configuration: it is the running application.
*
*       The lifecycle is decoupled from any particular `main`. Arduino cores
*       define `setup()`/`loop()` as program-level functions, but bare-metal and
*       RTOS vendors use a plain `main()`. Exposing them as ordinary `app::`
*       functions lets *any* entry point drive the app the same way:
*
*       - plain main (see main.cpp):
*         ```cpp
*         int main() { app::setup(); for (;;) app::loop(); }
*         ```
*       - an Arduino sketch:
*         ```cpp
*         void setup() { app::setup(); }
*         void loop()  { app::loop(); }
*         ```
*
* Put your actual startup and per-tick logic in app.cpp.
*/
#ifndef APP_HPP_
#define APP_HPP_

namespace app {

    /**
    * @brief One-time initialization. Runs once before the first `loop()`.
    *
    * Bring up hardware and transports, and start any always-on tasks (e.g.
    * `config::internal.register_task(global::task_id::...)`).
    */
    void setup();

    /**
    * @brief One iteration of the run loop. Call repeatedly (forever).
    *
    * Advances every running task one step (`config::manager.update()`), and -
    * when external comms are enabled - routes any arriving packets first.
    */
    void loop();

} // namespace app

#endif // APP_HPP_
'''

    @staticmethod
    def __app_cpp() -> str:
        return '''\
/**
* @file app.cpp
*
* @brief Your application's startup and per-tick logic.
*
* @note User-owned. This is where the app actually does things. It is a normal
*       translation unit (compiled once), so it is the right home for real logic -
*       unlike the header-only wiring in config/ that it draws on.
*/
#include "app.hpp"
#include "config/wiring.hpp"
// #include "config/router.hpp"   // uncomment once you enable external comms (see wiring.hpp)

namespace app {

    void setup() {
        // TODO: initialize hardware and transports.
        //
        // Start any always-on tasks here, e.g.:
        //   (void)config::internal.register_task(global::task_id::blink);
    }

    void loop() {
        // config::poll_inbound();     // uncomment with a router to service arriving packets
        config::manager.update();      // advance tasks, deliver results
    }

} // namespace app
'''

    @staticmethod
    def __schema_yaml() -> str:
        return '''\
# schema.yaml - your application's task schema, and the starting point for a
# new project. This is the one file the code generator reads.
#
# Generate from it with:
#   cmake --build build --target etask-generate
#
# which produces two things, owned differently:
#   sys/**             task scaffolds + the context tree + task.hpp - created
#                         ONCE, then yours to edit. Regenerating refreshes only the
#                         constructor signature, never your bodies.
#   generated/task_id.hpp the `global::task_id` enum - rewritten IN FULL every
#                         run. Never edit it by hand.
#
# You do NOT hand-maintain the task list: config/wiring.hpp builds the manager
# from generated/task_list.hpp, so a new task is picked up automatically.
#
# See examples/ upstream for a worked, multi-feature schema (scopes, abstract
# scopes, contexts, params and returns).
#
# `brief` and `description` are optional but encouraged: `brief` becomes the
# @brief on `task_id::<task>` and on the generated class; `description` adds the
# longer detail paragraph on the class. Documenting here documents the code.
#
# `concurrency: N` (optional, default 1) lets N instances of a task run at once -
# it becomes capacity<Task, N> in the generated task_list.

blink:
  type: task
  brief: toggle the status LED
  description: |
    Flips the on-board status LED. A single-shot task: it toggles once in
    on_execute() and immediately reports finished.
'''

    # =====================================================================
    # config/ : settings + bridging (namespace config)
    # =====================================================================

    @staticmethod
    def __wiring_hpp() -> str:
        return '''\
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
'''

    @staticmethod
    def __router_hpp() -> str:
        return '''\
/**
* @file router.hpp
*
* @brief How arriving packets are routed - the node's inbound dispatch.
*
* @note User-owned config, and the inbound half of external comms. Include and
*       use this only once you have defined a transport and an `external_channel`
*       (see config/wiring.hpp) - it references both. A node with no external
*       comms does not use this file at all.
*
* This is the one place that decides what happens to a packet the moment it
* arrives. The default routes etask command packets to the task manager (via
* `external_channel::dispatch`), but a handler can do anything - the router is
* just "a packet of type X arrived -> run this".
*
* ## The model
*
* `ecomm::router` polls one or more transport channels and, for each packet that
* arrives, calls the handler whose parameter type matches it. The packet types
* it watches for are read off the handlers themselves - you never name a type
* twice. One `on_channel(channel, handlers...)` group per channel; drain it each
* tick with `try_receive_any()`. It owns per-channel reassembly state, so it
* must persist across polls (the single `inline` instance below), driven from
* `app::loop()`.
*/
#ifndef CONFIG_ROUTER_HPP_
#define CONFIG_ROUTER_HPP_
#include <ecomm/fabric/router.hpp>
#include "wiring.hpp"
// #include "support/channels/uart_channel.hpp"   // your transport(s)

namespace config {

    /**
    * @brief The inbound router for this node.
    *
    * Watches `link` for this link's request packets and hands each to the manager via
    * `external_channel::dispatch`, which parses the etask request, runs the
    * requested manager operation, and sends any reply back through `link`.
    *
    * @note `link` and `external` are the instances you defined in wiring.hpp
    *       when enabling external comms.
    */
    inline auto router = ecomm::router{
        ecomm::on_channel(link,

            // --- default: etask command packets -> task manager ---
            [](generated::links::<name>::request_packet_t& packet) {
                external.dispatch(packet);
            }

            // --- add your own packet types here ---
            // A handler is just `[](some_packet_t& p) { ... }`; the router polls
            // `link` for every packet type its handlers declare. For example:
            //
            //   , [](telemetry_packet_t& p) {
            //         // do anything - store it, forward it, ignore the manager entirely
            //     }
            //
            // (a second link in schema.yaml gets its own packet types).
        )

        // --- add another link here ---
        // A second transport is a second on_channel(...) group, e.g.:
        //
        //   , ecomm::on_channel(wifi,
        //         [](generated::links::<name>::request_packet_t& p) { external.dispatch(p); }
        //     )
    };

    /**
    * @brief Drain every packet ready on every routed channel this tick.
    *
    * Call once per `app::loop()`. Returns after the router has dispatched
    * everything currently framable; partially-arrived packets wait for the next
    * call.
    */
    inline void poll_inbound() {
        while (router.try_receive_any()) { }
    }

} // namespace config

#endif // CONFIG_ROUTER_HPP_
'''

    # =====================================================================
    # hal/ : hardware drivers (namespace hal) - documented, not seeded
    # =====================================================================

    @staticmethod
    def __hal_readme() -> str:
        return '''\
# hal/ - hardware drivers

The hardware this node drives lives here: motors, sensors, GPIO, ADCs, radios -
anything that pokes a register or a pin. This directory is **yours**; the code
generator never writes into it. It ships empty on purpose - no forced example.

## What goes here

A driver is plain C++ (a class exposing the device's operations) in
`namespace hal`. Keep one device per header, and **nest freely** - the elib
convention is directories-in-directories, and a subdirectory becomes a nested
namespace:

```
hal/
  imu/
    mpu6050.hpp        -> namespace hal::imu     (class mpu6050)
  motor/
    brushless.hpp      -> namespace hal::motor   (class brushless)
```

Purely-software helpers (transports, buffers, codecs) belong in `support/`
instead - the split is a suggestion, not a rule; put things where they read best.
Anything non-trivial can be a `.hpp`/`.cpp` pair; the CMake build compiles every
`hal/**/*.cpp`.

## Including from anywhere

The project root is the include root (see `CMakeLists.txt`), so include a driver
by its **path from the project root**, from any file at any depth - never a
`../../` walk:

```cpp
#include "hal/motor/brushless.hpp"
```

## How a driver reaches a task

A driver is owned by a *context*, not a task. Put an instance in the user-owned
area of the scope's generated context (`sys/<scope>/context.hpp`):

```cpp
// in sys/arm/context.hpp, in the "add your own state" area:
#include "hal/motor/brushless.hpp"
...
struct context {
    hal::motor::brushless motor;   // owned here, shared by the scope's tasks
    ...
};
```

Every task in that scope receives `context&` and drives `ctx.motor`. Hardware is
constructed once, with the context, top-down - never inside a task.
'''

    # =====================================================================
    # support/ : software + linking helpers (namespace support) - documented
    # =====================================================================

    @staticmethod
    def __support_readme() -> str:
        return '''\
# support/ - software & linking helpers

Software that links parts together lives here: transports (serial, TCP, radio),
buffers, codecs, small protocol glue - as opposed to raw hardware drivers, which
go in `hal/`. This directory is **yours**; the code generator never writes into
it, and it ships empty on purpose - no forced example. (A transport straddles the
two worlds; it belongs here because what it *is* is a communication link. Prefer
it next to the hardware it pokes? Move it to `hal/` - the split is a suggestion,
not a rule.)

## What goes here

Plain C++ in `namespace support`, one thing per header, **nested freely** - the
elib convention is directories-in-directories, and a subdirectory becomes a
nested namespace:

```
support/
  channels/
    uart_channel.hpp   -> namespace support::channels  (class uart_channel)
  codecs/
    cobs.hpp           -> namespace support::codecs     (class cobs)
```

Anything non-trivial can be a `.hpp`/`.cpp` pair; the CMake build compiles every
`support/**/*.cpp`.

## Including from anywhere

The project root is the include root (see `CMakeLists.txt`), so include a helper
by its **path from the project root**, from any file at any depth - never a
`../../` walk:

```cpp
#include "support/channels/uart_channel.hpp"
```

## Writing a transport channel

A transport is an `ecomm::channels::channel<Impl>` (CRTP): the base handles
framing, validation and sealing; your `Impl` supplies only the raw byte I/O. For
a streaming link (UART, TCP byte stream) `Impl` provides three primitives:

```cpp
template<typename Packet> void        do_send(const Packet& p) noexcept;        // write sizeof(Packet) bytes
template<typename Packet> bool        do_try_receive(Packet& p) noexcept;       // read one whole framed packet
                          std::size_t do_receive_raw(std::byte* dst, std::size_t max) noexcept; // raw bytes (ecomm::router)
```

Defining the type instantiates nothing - you create the instance where you wire
it up (`config/wiring.hpp`) and hand it to an `external_channel` and/or an
`ecomm::router`. See the commented example there.
'''
