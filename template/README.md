# etask application template

A starter for an [etask](https://github.com/MarikTik/etask) project. Everything
here is meant to be **copied into your own project and then owned by you** - it
is the non-generated half of an etask app (build, config, task base, seed
schema). The generated half (the task tree in `sys/`, the `global::task_id` enum,
and the per-tier task typelists) is produced on demand and never shipped here.

## Layout

| path | what it is | who owns it |
|------|------------|-------------|
| `schema.yaml` | your task schema - the generator's input | you (edit freely) |
| `app.{hpp,cpp}` | `app::setup()` / `app::loop()` - the app's lifecycle | you |
| `main.cpp` | plain-`main` adapter that drives `app::setup/loop` | you |
| `config/` | the wiring and protocol, namespace `config::` | you |
| `config/protocol.hpp` | the wire packet type | you |
| `config/wiring.hpp` | the task manager + channels (composition root) | you |
| `config/router.hpp` | inbound packet dispatch (only with external comms) | you |
| `hal/` | your hardware drivers, namespace `hal::` (see `hal/README.md`) | you |
| `support/` | your software / linking helpers incl. transports, namespace `support::` (see `support/README.md`) | you |
| `CMakeLists.txt` | fetches etask, defines the generate step, builds the app | you |
| `sys/**` *(generated)* | the context tree + task scaffolds; **created once**, then yours | you, after generation |
| `sys/context.hpp` *(generated)* | `sys::context`, the composition root owning every subsystem | the generator - one-time |
| `sys/task.hpp` *(generated)* | the task base alias for this project | the generator - one-time |
| `generated/task_id.hpp` *(generated)* | the `global::task_id` enum; **rewritten every run** | the generator - never edit |
| `generated/task_list.hpp` *(generated)* | the per-tier task typelists (`instant_tasks`, `polled_tasks`, `stateful_tasks`); **rewritten every run** | the generator - never edit |

`etask/core` itself is fetched by CMake and never copied.

## First build

The build process is two steps: **scaffold** (lays down the non-generated half once),
then **generate** (produces the task tree and enums every time the schema changes).

**Scaffold (first time only):**
```sh
etask scaffold --out .
```
This creates `app.hpp`, `app.cpp`, `main.cpp`, `config/`, `hal/`, `support/`, and
`sys/task.hpp` - never overwriting files that already exist.

**Generate (every time you edit schema.yaml):**
```sh
etask generate schema.yaml \
    --out sys \
    --task-id generated/task_id.hpp \
    --task-list generated/task_list.hpp
```
This produces the context tree in `sys/`, and the always-rewritten `generated/` files.

**In CMake:** The `etask-generate` target runs the generate step. The scaffold is
typically run once during project setup.

```sh
cmake -S . -B build
cmake --build build --target etask-generate   # schema.yaml -> sys/ + generated/
cmake -S . -B build                            # re-configure so new sys/*.cpp are picked up
cmake --build build                            # build the app
```

A fresh copy does **not** build until you generate - there is no context tree, no
`global::task_id`, and no generated task lists yet. That is deliberate: nothing
in this directory can be clobbered by the generator.

## Adding a task

1. Add it to `schema.yaml` (a `brief` and `description` are encouraged - they
   become the task's documentation).
2. `cmake --build build --target etask-generate` - regenerates `sys/` (adding new
   task scaffolds, one-time context files, and nested scope contexts as the schema
   changes), and rewrites `generated/task_id.hpp` and `generated/task_list.hpp`.
3. Re-configure and build. **You do not touch `wiring.hpp`** - the manager is
   built from the generated `task_list`, so a new task is picked up automatically.

Regenerating never overwrites a task body you have edited - it only refreshes the
generated constructor signature (tagged with the `etask:sig` anchor) to match the
schema.

## Configuring the node

- **`config/protocol.hpp`** - the wire packet: size, topology, checksum.
- **`config/wiring.hpp`** - the composition root. The task manager (built from the
  generated `task_list`) and the `internal_channel` are live here. **External
  comms are opt-in**: a node that only runs tasks it starts itself needs none.
- **`hal/`** - hardware drivers a context owns (motors, sensors, etc.). Ships as a
  README, not a forced example: add your own, nested freely (`hal/imu/mpu6050.hpp`
  -> `namespace hal::imu`), and instantiate them in a scope's context.
- **`support/`** - software / linking helpers and transports (e.g. a UART channel,
  a codec). Also a README; add your own, nested freely, and instantiate in
  `wiring.hpp` or a context. Because the project root is the include root, both
  are includable by their top-level path from anywhere - `#include "hal/imu/mpu6050.hpp"`,
  no `../` - at any depth.
- **`config/router.hpp`** - what happens to an arriving packet, once you have a
  transport. The default routes etask command packets into the task manager; add
  handlers for your own packet types alongside it.
- **`app.cpp`** - your `setup()` (one-time init, start always-on tasks) and
  `loop()` (per-tick: route inbound packets, advance tasks).

See `examples/` upstream for worked, multi-feature projects (scopes, abstract
scopes, nested contexts, params and returns).
