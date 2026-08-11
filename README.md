# etask

**A header-only C++17 task framework for embedded systems, paired with a schema-driven C++ code generator.**

etask lets you describe a device's capabilities — its subsystems and the tasks
they can run — as a small YAML schema, and turns that schema into a typed,
hierarchical C++ project: task scaffolds, per-subsystem contexts, and the
enums/typelists that wire them into a runtime task manager. You own the task
bodies; the generator owns keeping the plumbing around them in sync.

etask is part of the **elib** family and builds directly on its siblings:
[etools](https://github.com/MarikTik/etools) (buffers, factories,
`meta::typelist`), [ecomm](https://github.com/MarikTik/ecomm) (wire packets,
channels, routing), and `eser` (etools' flat serializer, pulled in
transitively).

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [How it works](#how-it-works)
- [The schema format](#the-schema-format)
- [Command-line usage](#command-line-usage)
- [Ownership & regeneration model](#ownership--regeneration-model)
- [Quick start](#quick-start)
- [Examples](#examples)
- [Project layout](#project-layout)
- [Status / roadmap](#status--roadmap)
- [License](#license)

## Overview

Embedded task systems tend to accrete the same boilerplate on every project:
an enum of task IDs, a dispatch table mapping wire commands to constructors, a
tree of "subsystem" objects to hold hardware state, and hand-written glue
between all three that has to be kept in sync by hand as the device's
capability list grows.

etask splits that problem in two:

- A **runtime library** (`etask/core`) that supplies the pieces every task
  system needs regardless of what the device does: a task lifecycle interface,
  a manager that advances and garbage-collects tasks each tick, channels for
  delivering results, and a minimal application-layer wire protocol layered on
  top of `ecomm`'s packets.
- A **code generator** (`tools/src/schemav2`) that reads a `schema.yaml`
  describing your device's subsystems and tasks, and emits/maintains the C++
  project structure around them — task scaffolds, a composition tree of
  per-subsystem `context` objects, and the enum/typelist pair that bind
  everything into a `task_manager` instantiation.

The generator is deliberately conservative about what it touches. It creates
task bodies once and never overwrites your logic; only a few explicitly
tagged regions (a constructor signature, a list of managed child contexts,
schema-seeded doc comments) are kept in sync on later runs, and only until you
edit them yourself. See [Ownership & regeneration model](#ownership--regeneration-model).

## Features

- **Header-only C++17 runtime.** `#include <etask/...>`, link the `etask`
  INTERFACE target, done — no separate build step for the library itself.
- **Cooperative, non-blocking task lifecycle**: `on_start`, `on_execute`,
  `on_pause`, `on_resume`, `is_finished`, `on_complete`, all driven by a single
  `task_manager::update()` call per tick.
- **Schema-driven codegen**: describe subsystems and tasks once in YAML; get a
  typed C++ tree with matching structure.
- **Hierarchical, typed scopes.** A task declared under `legs.leg.muscle.motor`
  in the schema is generated as a C++ task that receives that exact scope's
  `context&` — no manual wiring of "which subsystem owns this task."
- **Abstract scopes.** Declare a subsystem shape once (e.g. "a leg") and
  instantiate it by name (`front_left`, `front_right`, ...); each instance gets
  its own concrete scope and context, with distinct, path-derived uids.
- **Generate-once, edit-forever task bodies.** Regeneration never clobbers
  logic you've written; see below.
- **"Sync until you touch it" documentation.** Doc comments seeded from the
  schema's `brief`/`description` stay in sync automatically — until you
  hand-edit them, at which point that block is frozen for the generator.
- **No forced license header** on generated or scaffolded code — that choice
  stays yours.
- **Root-as-include-root layout.** Every top-level directory (`sys/`, `hal/`,
  `support/`, `config/`) is includable by its own path from anywhere in the
  project, with no `../` — a subdirectory is just a nested namespace.

## Architecture

### The two halves

| | Runtime library (`etask/core`) | Code generator (`tools/src/schemav2`) |
|---|---|---|
| Language | C++17, header-only | Python |
| Ships as | An INTERFACE CMake target (`etask`) | A CLI (`python -m schemav2.cli`), also wired as a CMake custom target |
| Owns | Task lifecycle, task manager, channels, wire protocol | `schema.yaml` → C++ project structure |
| Changes | Rarely, as a dependency you pull via FetchContent | Run every time you edit `schema.yaml` |

### elib dependencies

etask's CMakeLists.txt fetches its siblings via `FetchContent` and links them
into the `etask` INTERFACE target, so a consumer that links `etask` gets the
whole chain transitively:

```
etask  →  ecomm  →  etools  →  eser
```

- **etools** — generic building blocks: `etools::memory::buffer`/`buffer_view`,
  `etools::factories::dispatch_factory` (the zero-allocation, uid-keyed
  registry backing `task_manager`), and `etools::meta::typelist` (the
  compile-time list type the generated task set is expressed as).
- **ecomm** — the communication layer: `ecomm::protocol::packet` (the raw wire
  frame etask's `protocol::request`/`reply` parse and build on top of),
  `ecomm::channels::channel` (the CRTP transport interface), and
  `ecomm::fabric::router` (inbound packet dispatch).
- **eser** — etools' flat, tagless serializer; used by `task_unpack_adapter` to
  unpack a wire payload into a task's typed constructor arguments.

### Runtime library components (`etask/core`)

- **`etask::core::task<TaskID>`** (`etask/core/task.hpp`) — the task base
  class. Lifecycle hooks: `on_start()`, `on_execute()`, `is_finished()`,
  `on_complete(completion_reason)` (returns an `etask::core::outcome` — write
  `return {r1, r2, ...}` and the values are packed straight into the outgoing
  packet, no heap, no copy), `on_pause()`, `on_resume()`. All are virtual with
  empty/trivial defaults; you override only what a given task needs. `TaskID` is
  your project's task-identifying type (typically an enum) — the manager uses it
  to route by uid.
- **`etask::core::task_manager<Tasks...>`** and
  **`task_manager_from_t<typelist<Tasks...>>`** (`etask/core/task_manager.hpp`)
  — owns a `dispatch_factory`-backed registry of task types, advances every
  registered instance each `update()`, and delivers results through a
  `channel_t`. `task_manager_from_t` bridges an `etools::meta::typelist` (the
  generator's output shape) to the manager's variadic template form, so the
  generated task list and the hand-written manager instantiation stay
  decoupled — regenerating the list never rewrites your wiring.
- **`etask::core::channels`** (`etask/core/channels/`) —
  `internal_channel<Manager>` delivers results for tasks this node starts
  itself; `external_channel<Packet, Hub, Manager>` bridges tasks arriving over
  the wire through an `ecomm` hub/channel.
- **`etask::core::protocol`** (`etask/core/protocol/`) — etask's
  application-layer schema layered on top of an `ecomm::protocol::packet`
  payload: `directive` (a single command+reason byte — which manager operation
  to invoke, and for `complete_task`, why), `request` (a structured, parsed
  view over an incoming payload), `reply` (builds an outgoing payload from a
  task's uid/status/result).
- **`etask::core::task_unpack_adapter<Task, Args...>`** /
  **`scoped_task_unpack_adapter<Task, ScopeFn, Args...>`**
  (`etask/core/task_unpack_adapter.hpp`) — wraps a task with a native-typed
  constructor (e.g. `spin(std::uint8_t duty, context&)`) so it can instead be
  constructed from a raw `buffer_view`, by unpacking the payload into typed
  arguments (and, for the scoped variant, binding a scope's `context&` via a
  nullary accessor function). This is the adapter the generated `task_list`
  will apply automatically — see [Status / roadmap](#status--roadmap).

## How it works

A typical project directory is built in two passes:

1. **`scaffold`** lays down the *non-generated* half once: the entry point,
   app lifecycle, config, and placeholders for hardware/software helpers.
   Existing files are never touched on a re-run.
2. **`generate`** reads `schema.yaml` and produces/updates the *generated*
   half: a `sys/` tree mirroring the schema's scope structure, a `context`
   object per scope (the **context composition tree** — every scope owns its
   own state and its child scopes' contexts as members, so the whole tree is
   built once, top-down, from a single root object `sys::context`), one task
   scaffold per schema task, `sys/task.hpp` (the project's task base alias,
   emitted once), and two always-rewritten files: `generated/task_id.hpp` (the
   `global::task_id` enum) and `generated/task_list.hpp` (the
   `generated::task_list` typelist, which `task_manager_from_t` turns into a
   manager instantiation).

`generate` also maintains **`.schema.uids.json`**, the *uid ledger*: the record
of which wire id each task owns. A uid is a protocol identifier — peers put it
in requests and match it in replies — so it must not drift when the schema is
edited. The ledger makes uid assignment a lookup: a task that already has an id
keeps it, and only a genuinely new task gets one derived from its path. It also
pins the uid width (which only ever grows) and keeps the ids of deleted tasks
reserved, so a new task can never inherit an id an old peer still remembers.
**Commit it next to `schema.yaml`** — it is as much a part of the wire contract
as the schema. It is a dotfile because it is generator-maintained bookkeeping you
never hand-edit, *not* because it is disposable: don't add it to `.gitignore`, or
every fresh clone re-derives ids from scratch and you are back to uids that drift. If a schema edit does force an id to move (you pinned an
explicit `uid:` that another task held), the generator says so on stderr rather
than moving it silently. `--no-uid-ledger` derives ids from the schema alone,
for throwaway inspection.

Emission is prepare-then-commit: every file is rendered and reconciled in
memory before anything is written, so a failure part-way through — a mangled
`//! etask:sig` anchor, say — leaves the project exactly as it was rather than
half-regenerated.

A generated project looks like this:

```
<project>/
├── CMakeLists.txt          ← fetches etask, defines the generate step
├── main.cpp                ← entry point driving app::setup()/app::loop()
├── app.hpp / app.cpp       ← the app lifecycle                    (namespace app,     yours)
├── schema.yaml             ← the generator's input
├── .schema.uids.json       ← the uid ledger: each task's wire id, kept stable (commit it)
├── config/                                                        (namespace config,  yours)
│   ├── protocol.hpp        ← the wire packet type
│   ├── wiring.hpp          ← composition root: task manager + channels
│   └── router.hpp          ← inbound packet dispatch (external comms only)
├── hal/                    ← your hardware drivers                (namespace hal,     yours)
├── support/                ← software/linking helpers, transports (namespace support, yours)
├── sys/                    ← generated task tree + context tree             (namespace sys,     generated once)
│   ├── context.hpp         ← sys::context, the composition root
│   ├── task.hpp            ← the task<global::task_id> alias, emitted once
│   └── <scope>/…           ← one directory per scope, task .hpp/.cpp per task
└── generated/                                                     (rewritten every run)
    ├── task_id.hpp         ← global::task_id enum
    └── task_list.hpp       ← generated::task_list typelist
```

A root-level task (parented directly under the schema root, not under any
scope) receives `sys::context&` — the composition root — so it can reach every
subsystem; this is how a `reboot`- or `failsafe`-style task coordinates across
the whole device.

## The schema format

The schema is a tree of three node kinds — `scope`, `abstract_scope`, and
`task` — declared under a top-level mapping of names to nodes. A short excerpt
from [`schema/schema.yaml`](schema/schema.yaml) (a worked dog-mimicking-robot
example):

```yaml
legs:
  type: scope
  description: locomotion subsystem grouping all four legs
  children:
    leg:
      type: abstract_scope
      description: one leg; expanded into the four physical legs
      instances: [front_left, front_right, rear_left, rear_right]
      children:
        calibrate:
          type: task
          description: task ON the leg subsystem — receives the leg scope
          params: { tolerance: float }
          returns: { ok: bool }
        muscle:
          type: abstract_scope
          description: a muscle group within a leg
          instances: [hip, knee]
          children:
            motor:
              type: abstract_scope
              description: a motor within a muscle; written once, runs on each
              instances: [motor1, motor2]
              children:
                on:
                  type: task
                  params: { intensity: uint8 }
                  returns: { ok: bool }
                off:
                  type: task
                  params: {}

system:
  type: scope
  description: board-level controls
  children:
    reboot:
      type: task
      description: explicit uid; parent is a scope so it receives `system`
      uid: 200
      params: {}
```

Key points:

- **`scope`** is a plain namespace/subsystem grouping; **`abstract_scope`**
  is a template expanded once per name in `instances`, each expansion getting
  its own concrete scope, context, and a distinct, path-hashed uid.
- **`task`** is a leaf unit of work. `params` and `returns` are ordered maps
  of `name: type` — order is the wire contract, since the codec is flat and
  tagless.
- `brief`/`description` are optional and become doc comments on the generated
  task (see [Ownership & regeneration model](#ownership--regeneration-model)
  for how those stay in sync).
- `uid` is optional; when omitted, one is derived from the task's path on the
  task's *first* generation and then held in the uid ledger (see below), so it
  does not move as the schema grows. `concurrency: N` reserves N concurrent
  slots for a task (surfaced to the runtime via
  `etools::factories::utils::capacity<Task, N>`).
- A JSON meta-schema describing this format lives under `schema/meta/`.

## Command-line usage

The generator is a Python CLI, invoked as a module (or via the
`etask-generate` CMake target that scaffolded projects define):

```sh
PYTHONPATH=tools/src python -m schemav2.cli <command> [args]
```

| command | purpose |
|---|---|
| `scaffold --out <dir>` | Lay down the non-generated half of a project once: root `app.{hpp,cpp}`/`main.cpp`/`CMakeLists.txt`, `config/{protocol,wiring,router}.hpp`, and `hal/`/`support/` READMEs. Files that already exist are kept untouched. |
| `generate <schema> --out <dir>/sys --task-id <dir>/generated/task_id.hpp --task-list <dir>/generated/task_list.hpp` | Produce/update the generated half from a schema: the `sys/` task and context tree, and the always-rewritten `task_id.hpp`/`task_list.hpp`. Maintains the uid ledger (`--uid-ledger <path>` to relocate it, `--no-uid-ledger` to skip it). |
| `rename <schema> --out <dir>/sys <task> <new_name>` | Rename a concrete task (dotted schema path, e.g. `system.reboot`) in both the schema and its generated files, carrying its uid over in the ledger so the rename stays wire-compatible. |

Example, matching the layout under `examples/humanoid/`:

```sh
PYTHONPATH=tools/src python -m schemav2.cli generate examples/humanoid/schema.yaml \
    --out       examples/humanoid/sys \
    --task-id   examples/humanoid/generated/task_id.hpp \
    --task-list examples/humanoid/generated/task_list.hpp
```

## Ownership & regeneration model

etask's generator is built around one rule: **it should be safe to run
`generate` at any time, on a project you've been editing by hand, without
losing anything.**

- **Generate-once task bodies.** Each schema task produces a `.hpp`/`.cpp`
  scaffold the first time it's generated. After that, the file is yours — the
  generator will not overwrite the logic you write into it.
- **Surgical regeneration.** On later runs, only a few explicitly tagged
  regions are refreshed to match the schema:
  - `//! etask:sig` — the constructor signature, kept in sync with the
    schema's `params`.
  - `//! etask:managed` — the list of child contexts a scope's `context` owns.
  - `//! etask:doc` — doc-comment blocks.
- **Doc comments are "sync until you touch it."** A task's schema-seeded
  `@brief`/`@description` are regenerated automatically as the schema changes
  — until you hand-edit that comment block yourself, at which point the
  generator recognizes the edit and freezes it: your wording wins from then
  on.
- **No license is forced** on generated or scaffolded files. What license (if
  any) your project's own code carries is entirely your decision.
- **The task set is generated; the manager instantiation is yours.**
  `generated::task_list` (a typelist) is rewritten on every `generate`, but
  `config/wiring.hpp` builds the manager from it once, via
  `task_manager_from_t<generated::task_list>`. Adding a task to the schema and
  regenerating never requires editing `wiring.hpp`.
- **Include-root layout.** The project root is the include root, so any
  top-level directory is includable by its own path from anywhere, with no
  `../` — e.g. `#include "hal/imu/mpu6050.hpp"` regardless of the includer's
  depth.

## Quick start

Start from [`template/`](template/), which mirrors what `scaffold` produces:

**1. Scaffold the non-generated half (first time only):**

```sh
PYTHONPATH=tools/src python -m schemav2.cli scaffold --out .
```

This creates `app.hpp`, `app.cpp`, `main.cpp`, `config/`, `hal/`, `support/` —
without overwriting anything that already exists.

**2. Generate the task tree (every time `schema.yaml` changes):**

```sh
PYTHONPATH=tools/src python -m schemav2.cli generate schema.yaml \
    --out sys \
    --task-id generated/task_id.hpp \
    --task-list generated/task_list.hpp
```

**3. Pull in etask via CMake `FetchContent`** (this is what the scaffolded
`CMakeLists.txt` does):

```cmake
include(FetchContent)
FetchContent_Declare(
  etask
  GIT_REPOSITORY https://github.com/MarikTik/etask.git
  GIT_TAG        main   # pin to a release tag for reproducible builds
)
FetchContent_MakeAvailable(etask)

target_link_libraries(your_app PRIVATE etask)
```

Linking `etask` transitively brings in `ecomm` and `etools`; `#include
<etask/...>` headers become available immediately.

**4. Build:**

```sh
cmake -S . -B build
cmake --build build --target etask-generate   # schema.yaml -> sys/ + generated/
cmake -S . -B build                            # re-configure to pick up new sys/*.cpp
cmake --build build
```

A freshly scaffolded project intentionally does not build until step 2/4 has
run once — there is no context tree, no `global::task_id`, and no
`generated::task_list` yet.

See [`template/README.md`](template/README.md) for the full walkthrough,
including how to add a task and configure `hal/`, `support/`, and
`config/router.hpp`.

## Examples

Two complete, worked schemas under [`examples/`](examples/), each showing the
generator's output on a differently-shaped device:

- **[`examples/humanoid/`](examples/humanoid/)** — a small humanoid robot:
  paired limb subsystems (`arms`/`legs`) built from abstract scopes, a
  root-level `reboot` task with an explicit uid, concurrent tasks via
  `capacity<...>`.
- **[`examples/quadcopter/`](examples/quadcopter/)** — a flight controller: a
  four-rotor array, a read-only sensor suite (`imu`/`baro`/`gps`), a
  navigation layer, and a root-level `failsafe` task that reaches every rotor
  through the composition root.

Both are described in the guide's ["Status / roadmap"](#status--roadmap)
sense: complete and correct end-to-end, pending the one remaining pipeline
step described below.

## Project layout

| path | what it is |
|---|---|
| [`etask/`](etask/) | The header-only runtime library (`etask::core`) |
| [`tools/`](tools/) | The Python schema-driven code generator (`schemav2`) and its tests |
| [`schema/`](schema/) | A worked example schema (`schema.yaml`) and the JSON meta-schema |
| [`template/`](template/) | A starter project mirroring `scaffold`'s output, meant to be copied |
| [`examples/`](examples/) | Complete worked examples: [`humanoid`](examples/humanoid/), [`quadcopter`](examples/quadcopter/) |
| [`CMakeLists.txt`](CMakeLists.txt) | Defines the `etask` INTERFACE target and its `FetchContent` dependencies |

## Status / roadmap

The runtime library and the code generator are both built and tested — the
Python test suite currently passes all 133 tests. Everything described above
(scaffold/generate, the context composition tree, task scaffolds, surgical
regeneration, sync-until-touched docs) is implemented and working.

**One step remains before a generated project fully builds and links:** the
generated `generated::task_list` does not yet wrap each task in
`task_unpack_adapter`/`scoped_task_unpack_adapter` (with generated scope
accessor functions for the scoped case). Schema-generated tasks have
native-typed constructors (e.g. `spin(std::uint8_t duty, context&)`), while
`task_manager` currently requires every registered task to be constructible
from a single `etools::memory::buffer_view`. Until the generator emits the
adapter-wrapped list, instantiating the manager in `config/wiring.hpp` stops
at a documented `static_assert` — see the `@warning` on `manager_t` in that
file, and the "Notes on buildability" section of each example's README. This
is the clearly-scoped next step in the pipeline, not an open design question:
the adapter types themselves (`etask/core/task_unpack_adapter.hpp`) already
exist and are exercised by the runtime library's own tests; what remains is
having the generator emit the wrapped typelist entries and per-scope accessor
functions.

## License

This project is licensed under the **MIT License** — free for commercial and
non-commercial use, modification, and distribution, provided the copyright and
permission notice are retained.

Copyright (c) 2025 **Mark Tikhonov**  
📧 mtik.philosopher@gmail.com

See the [LICENSE](./LICENSE) file for the full legal text.
