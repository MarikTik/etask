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
- [The Python client](#the-python-client)
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
- A **code generator** (`etask.schema`, in [`etask-python/`](etask-python/)) that reads a `schema.yaml`
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
- **A generated Python client.** The same schema also produces an async client
  (`--python`) so a PC or Raspberry Pi can launch tasks and decode their typed
  results — several in flight at once — over Wi-Fi or serial. See
  [The Python client](#the-python-client).
- **Root-as-include-root layout.** Every top-level directory (`sys/`, `hal/`,
  `support/`, `config/`) is includable by its own path from anywhere in the
  project, with no `../` — a subdirectory is just a nested namespace.

## Architecture

### The two halves

| | Runtime library (`etask/core`) | Python half (`etask-python/`) |
|---|---|---|
| Language | C++17, header-only | Python |
| Ships as | An INTERFACE CMake target (`etask`) | A pip distribution (`etask`): the async client, plus the `etask` CLI under the `codegen` extra; also wired as a CMake custom target |
| Owns | Task lifecycle, task manager, channels, wire protocol | `schema.yaml` → C++ project + Python bindings; driving a device from a PC |
| Changes | Rarely, as a dependency you pull via FetchContent | The generator runs every time you edit `schema.yaml`; the client is a normal dependency of your Python code |

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
│   ├── wiring.hpp          ← composition root: task manager + channels
│   └── router.hpp          ← inbound packet dispatch (external comms only)
├── hal/                    ← your hardware drivers                (namespace hal,     yours)
├── support/                ← software/linking helpers, transports (namespace support, yours)
├── sys/                    ← generated task tree + context tree             (namespace sys,     generated once)
│   ├── context.hpp         ← sys::context, the composition root
│   ├── task.hpp            ← the task<global::task_id> alias, emitted once
│   └── <scope>/…           ← one directory per scope, task .hpp/.cpp per task
├── generated/                                                     (rewritten every run)
│   ├── task_id.hpp         ← global::task_id enum
│   ├── task_list.hpp       ← the per-tier task typelists + budgets
│   └── links.hpp           ← one packet type per direction, per link
└── python/                 ← the client a PC/Pi drives the device with (rewritten every run)
    └── tasks.py            ← uids, typed calls, one dataclass per result shape
```

A root-level task (parented directly under the schema root, not under any
scope) receives `sys::context&` — the composition root — so it can reach every
subsystem; this is how a `reboot`- or `failsafe`-style task coordinates across
the whole device.

## The schema format

The schema has two top-level sections. **`system:`** holds the device — a tree
of three node kinds, `scope`, `abstract_scope`, and `task` — and is required.
**`budget:`** is optional and sizes the task managers' storage; see below. Later
settings will join them as further named sections, which is why the node tree
lives in a section of its own rather than at the top level.

A short excerpt from [`schema/schema.yaml`](schema/schema.yaml) (a worked
dog-mimicking-robot example):

```yaml
system:
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
            type: oneshot_task
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
                    type: oneshot_task
                    params: { intensity: uint8 }
                    returns: { ok: bool }
                  off:
                    type: instant_task

  board:
    type: scope
    description: board-level controls
    children:
      reboot:
        type: instant_task
        description: explicit uid; parent is a scope so it receives `board`
        uid: 200
```

`system:` is schema framing only — it adds no C++ namespace level, so a task
declared directly under it is still `sys::reboot`, not `sys::system::reboot`.
A scope may itself be named `system` without ambiguity.

Key points:

- **`scope`** is a plain namespace/subsystem grouping; **`abstract_scope`**
  is a template expanded once per name in `instances`, each expansion getting
  its own concrete scope, context, and a distinct, path-hashed uid.
- **`task`** is a leaf unit of work. `params` and `returns` are ordered maps
  of `name: type` — order is the wire contract, since the codec is flat and
  tagless.
- **`returns` may be keyed by status.** A reply carries `[uid][status][result]`,
  so the status byte is already a discriminator: a task can return *different
  values depending on how it ended*, and the schema says which shape goes with
  which status.

  ```yaml
  fix:
    type: task
    params: { timeout_ms: uint32 }
    returns:                                    # one shape per status
      finished:     { lat: double, lon: double, sats: uint8 }
      task_timeout: { waited_ms: uint32, sats_seen: uint8 }
  ```

  A plain `returns: { ax: float }` is shorthand for the `finished` shape alone.
  The two forms are told apart by the *values* — type strings mean a single
  shape, nested mappings mean status-keyed — so a result field may still be
  called `finished` without being mistaken for a status. Mixing the two in one
  mapping is an error rather than a guess.

  Keys are `status_code` enumerator names, with `finished`/`aborted` as aliases
  for `task_finished`/`task_aborted`, plus `custom(0x71)` for your own codes.
  Manager/API codes cannot key a shape — they mean the manager *rejected the
  request and no task ran*, so no result could arrive. That includes `ok`, which
  is `outcome`'s "the task chose no status" sentinel. On the device, a non-default
  shape is returned with `outcome{...}.with_status(code)`.
- `brief`/`description` are optional and become doc comments on the generated
  task (see [Ownership & regeneration model](#ownership--regeneration-model)
  for how those stay in sync).
- `uid` is optional; when omitted, one is derived from the task's path on the
  task's *first* generation and then held in the uid ledger (see below), so it
  does not move as the schema grows. `concurrency: N` reserves N concurrent
  slots for a task (surfaced to the runtime via
  `etools::factories::utils::capacity<Task, N>`).
- **`budget:` sizes the managers, and is where measurement pays.** Each managed
  tier reserves storage for as many live task records as its budget allows,
  held *inline* — the task managers allocate nothing, ever. Omit the section and
  each tier reserves the sum of its tasks' `concurrency`: every task running at
  its own limit at once. That is the only bound the schema alone can justify,
  and it is usually far more than a device really runs — the worked quadcopter
  defaults to 21 polled records for an aircraft whose measured peak is eight.

  ```yaml
  budget:
    polled: 8       # at most 8 polled/oneshot tasks live at once
    stateful: 1     # a paused task still holds its record
  ```

  Declaring less than the sum is a claim about measured behaviour: past it, a
  launch is refused with `task_budget_exhausted` (distinct from
  `task_limit_reached`, which means that one task's own slots are full). There
  is deliberately no fairness policy, so once the budget binds, task types
  compete first-come-first-served. Declaring *more* than the sum is rejected —
  those records could never be occupied. An `instant_task` takes no budget: it
  occupies no storage and runs to completion inside the call that delivers it.
- **`links:` describes the wires, and sizes the frames.** A board may speak over
  several links with opposite guarantees — a radio loses frames silently, a TCP
  socket does not — so each declares its own transport and gets its own packet
  types, generated into `generated/links.hpp`:

  ```yaml
  links:
    radio:
      transport: wifi
      topology: network
      checksum: crc16
      reliable: true       # retransmit: a raw datagram path drops frames
    bench:
      transport: uart      # point_to_point, crc16, reliable — all defaulted
  ```

  Everything omitted is defaulted from the transport, and contradictions are
  build errors rather than silent waste: a checksum or a reliability layer on
  `tcp` is refused, because the transport already provides both.

  **You never choose a packet size.** Each link gets *two* packet types, sized
  independently — a request carries a task's arguments, a reply carries its
  result, and either may be the larger. In the worked quadcopter the same schema
  yields a 40-byte reply frame on `radio` (6-byte addressed header) and 32 on
  `bench` (4-byte header), with no number written by hand. Sizes are rounded
  identically on every target, so a PC client and an ESP32 built from one schema
  always agree on the wire.
- **The two ends check they agree, before anything else.** Every generated
  project carries an eight-byte fingerprint of its whole wire contract — every
  uid, argument list, result shape and link policy — emitted as
  `generated::schema_fingerprint` in C++ and `SCHEMA_FINGERPRINT` in the Python
  client. On connect the peers exchange it in a fixed 14-byte preamble and
  compare.

  The failure this exists for is the quiet one. Two builds from *different*
  schemas can agree on every byte of frame layout and none of the meaning: the
  frames parse, the checksum passes, and the device runs the wrong task with
  plausible-looking arguments. A mismatch now refuses that link
  (`status_code::schema_mismatch`) and logs both fingerprints, while the device's
  other links keep working.

  The preamble is sent raw rather than in a packet, because two peers that
  disagree about a header cannot use a normal frame to say so. Both halves are
  opt-in — a link built without a fingerprint, or a transport with no raw byte
  path, behaves exactly as before.
- A JSON meta-schema describing this format lives under `schema/meta/`.

## Command-line usage

The generator is a Python CLI. Installed (`pip install etask[codegen]`) it is
just `etask`; from a checkout, with nothing installed, it is the same code run as
a module — which is what the `etask-generate` CMake target scaffolded projects
define does:

```sh
etask <command> [args]                                        # installed
PYTHONPATH=etask-python python -m etask.schema.cli <command>  # from a checkout
```

| command | purpose |
|---|---|
| `scaffold --out <dir>` | Lay down the non-generated half of a project once: root `app.{hpp,cpp}`/`main.cpp`/`CMakeLists.txt`, `config/{wiring,router}.hpp`, and `hal/`/`support/` READMEs. Files that already exist are kept untouched. |
| `generate <schema> --out <dir>/sys --task-id <dir>/generated/task_id.hpp --task-list <dir>/generated/task_list.hpp --links <dir>/generated/links.hpp` | Produce/update the generated half from a schema: the `sys/` task and context tree, and the always-rewritten `task_id.hpp`/`task_list.hpp`/`links.hpp`. Maintains the uid ledger (`--uid-ledger <path>` to relocate it, `--no-uid-ledger` to skip it), and with `--python <path>` also emits the Python client bindings. |
| `rename <schema> --out <dir>/sys <task> <new_name>` | Rename a concrete task (dotted schema path, e.g. `system.reboot`) in both the schema and its generated files, carrying its uid over in the ledger so the rename stays wire-compatible. |

Example, matching the layout under `examples/humanoid/`:

```sh
etask generate examples/humanoid/schema.yaml \
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

## The Python client

A device is only half a system: something has to *ask* it to do things. That
peer is usually a PC, a Raspberry Pi, or a test runner speaking Python, so the
schema generates one.

Two pieces, split the same way the C++ side is:

- **`etask-python/`** — the hand-written runtime, byte-exact with `etask/core`:
  the status/directive enums, the flat value codec, the request/reply payload
  layout, and an async `Client`. It is to `etask/core` what `ecomm-python` is to
  `ecomm`, and it is versioned once rather than copied into every project.
- **`python/tasks.py`** — generated per project by `--python`. Pure projection:
  uids, one typed `async` call per task, and one frozen dataclass per declared
  result shape. No wire logic, so fixing the protocol never means regenerating
  your projects.

```python
async with Client(channel, uid_bytes=Tasks.UID_BYTES, receiver_id=1) as client:
    tasks = Tasks(client)

    # Launching does not block, so these two fly together.
    fix, altitude = await asyncio.gather(
        tasks.sensors.gps.fix(timeout_ms=5000),
        tasks.sensors.baro.read_altitude(),
    )

    match fix:
        case tasks.sensors.gps.fix.Finished(lat=lat, lon=lon, sats=sats):
            ...
        case tasks.sensors.gps.fix.Timeout(waited_ms=waited):
            ...
```

Which dataclass you get is decided by the reply's status byte — the schema's
status-keyed `returns:` on one end, `outcome::with_status(...)` on the other. A
completion the schema does not describe arrives as `UndeclaredResult` rather than
an error; a manager *rejection* (unknown uid, concurrency cap) raises
`TaskRejected`, since in that case no task ran at all.

**What the wire cannot tell you.** A reply is `[uid][status][result]` with no
invocation id, so replies are matched to launches FIFO per uid — exact at
`concurrency: 1`, best-effort above it — and `pause`/`resume`/`complete` succeed
silently, because the firmware answers those only when they fail. Both are
handled explicitly by the client and documented in
[`etask-python/README.md`](etask-python/README.md).

`ecomm` is not on PyPI yet, so install it from a checkout:

```sh
pip install -e ../ecomm/ecomm-python
pip install -e etask-python
```

## Quick start

Start from [`template/`](template/), which mirrors what `scaffold` produces:

**1. Scaffold the non-generated half (first time only):**

```sh
etask scaffold --out .
```

This creates `app.hpp`, `app.cpp`, `main.cpp`, `config/`, `hal/`, `support/` —
without overwriting anything that already exists.

**2. Generate the task tree (every time `schema.yaml` changes):**

```sh
etask generate schema.yaml \
    --out sys \
    --task-id generated/task_id.hpp \
    --task-list generated/task_list.hpp \
    --python python/tasks.py        # optional: the Python client for this device
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
| [`etask-python/`](etask-python/) | Everything Python, as one distribution: the `etask` client runtime, the `etask.schema` code generator behind it, the `etask` CLI, and their tests |
| [`schema/`](schema/) | A worked example schema (`schema.yaml`) and the JSON meta-schema |
| [`template/`](template/) | A starter project mirroring `scaffold`'s output, meant to be copied |
| [`examples/`](examples/) | Complete worked examples: [`humanoid`](examples/humanoid/), [`quadcopter`](examples/quadcopter/) |
| [`CMakeLists.txt`](CMakeLists.txt) | Defines the `etask` INTERFACE target and its `FetchContent` dependencies |

## Status / roadmap

The runtime library and the code generator are both built and tested — the
Python test suite currently passes all 299 tests. Everything described above
(scaffold/generate, the context composition tree, task scaffolds, surgical
regeneration, sync-until-touched docs) is implemented and working.

**The pipeline is closed end to end:** both worked examples under
[`examples/`](examples/) compile *and link* into complete binaries from their
schema alone. The payload-unpacking step that used to block this is done —
each manager wraps its own tasks in `task_unpack_adapter` /
`scoped_task_unpack_adapter` via `detail::registered_t`, so a schema-generated
task with a native-typed constructor (e.g. `spin(std::uint8_t duty, context&)`)
is constructible from a wire payload without the generated task lists having to
name the adapter at all.

The task managers allocate nothing: each holds its live-task records in inline
storage sized by its tier's `budget:` (see [the schema
format](#the-schema-format)), so there is no heap anywhere on a task's path
from the wire to its result.

Not yet done, in rough order of usefulness: on-device benchmarks (per-task
tick cost, per-task RAM, WiFi round-trip); the open items in
[`project/audit-2026-08.md`](project/audit-2026-08.md), chiefly the `rename`
regex and a compile-time guard that a task's result fits its packet.

## License

This project is licensed under the **MIT License** — free for commercial and
non-commercial use, modification, and distribution, provided the copyright and
permission notice are retained.

Copyright (c) 2025 **Mark Tikhonov**  
📧 mtik.philosopher@gmail.com

See the [LICENSE](./LICENSE) file for the full legal text.
