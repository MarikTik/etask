# etask application template

A starter for an [etask](https://github.com/MarikTik/etask) project. Everything
here is meant to be **copied into your own project and then owned by you** - it
is the non-generated half of an etask app (build, config, task base, seed
schema). The generated half (the `global::task_id` enum, the `generated::task_list`
typelist, and your task scaffolds) is produced on demand and never shipped here.

## Layout

| path | what it is | who owns it |
|------|------------|-------------|
| `schema.yaml` | your task schema - the generator's input | you (edit freely) |
| `config/` | the wiring, in namespace `config::` | you |
| `config/protocol.hpp` | the wire packet type | you |
| `config/transport/` | your physical channels (one header each) | you |
| `config/wiring.hpp` | the manager + channels (composition root) | you |
| `config/router.hpp` | inbound packet dispatch (only with external comms) | you |
| `config/app.{hpp,cpp}` | `config::setup()` / `config::loop()` - the app's lifecycle | you |
| `tasks/task.hpp` | the task base alias for this project | you |
| `main.cpp` | plain-`main` adapter that drives `config::setup/loop` | you |
| `CMakeLists.txt` | fetches etask, defines the generate step, builds the app | you |
| `tasks/**` *(generated)* | one scaffold per task; **created once**, then yours | you, after generation |
| `generated/task_id.hpp` *(generated)* | the `global::task_id` enum; **rewritten every run** | the generator - never edit |
| `generated/task_list.hpp` *(generated)* | the `generated::task_list` typelist; **rewritten every run** | the generator - never edit |

`etask/core` itself is fetched by CMake and never copied.

## First build

```sh
cmake -S . -B build
cmake --build build --target etask-generate   # schema.yaml -> tasks/ + generated/
cmake -S . -B build                            # re-configure so new tasks/*.cpp are picked up
cmake --build build                            # build the app
```

A fresh copy does **not** build until you generate - there are no tasks, no
`global::task_id`, and no `generated::task_list` yet. That is deliberate: nothing
in this directory can be clobbered by the generator.

## Adding a task

1. Add it to `schema.yaml` (a `brief` and `description` are encouraged - they
   become the task's documentation).
2. `cmake --build build --target etask-generate` - creates `tasks/<name>.hpp/.cpp`
   (your logic goes in the `.cpp`) and rewrites `generated/task_id.hpp` and
   `generated/task_list.hpp`.
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
- **`config/transport/`** - your physical channels (UART/TCP/radio/...), one header
  each. Nothing is instantiated by default - you create an instance in `wiring.hpp`
  only for the transports this node actually uses.
- **`config/router.hpp`** - what happens to an arriving packet, once you have a
  transport. The default routes etask command packets into the task manager; add
  handlers for your own packet types alongside it.
- **`config/app.cpp`** - your `setup()` (one-time init, start always-on tasks) and
  `loop()` (per-tick: route inbound packets, advance tasks).

See `examples/` upstream for a worked, multi-feature schema (scopes, abstract
scopes, contexts, params and returns).
