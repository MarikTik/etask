# quadcopter — a second worked etask example

A quadcopter flight controller, generated from one schema. It is deliberately a
different *shape* from the [humanoid](../humanoid/) example: there the tree is
limb-pairs (arms/legs); here it is a rotor **array** feeding a controller, a
read-only sensor suite, and a navigation layer that commands them. This is a
**complete, near-buildable project** showing the full integration path.

## The machine

- `rotors` → `rotor` *(abstract, expanded to `fl`/`fr`/`rl`/`rr`)* → `set_thrust`
  (all four spin together → `capacity<…, 4>`), `stop`.
- `sensors` → `imu` → `read` (six axes), `baro` → `read_altitude`,
  `gps` → `fix` (positional returns: `lat, lon, sats`).
- `nav` → `fly_to`, `hold`, `land`.
- `failsafe` — a root-level task (uid 255). It receives `sys::context` and,
  through it, reaches **every** rotor to cut thrust. That is the whole reason a
  system-level task is handed the composition root rather than one subsystem.

## Layout

| path | what it is |
|------|------------|
| `schema.yaml` | the input — the whole craft in one file |
| `app.{hpp,cpp}` | the flight controller's setup and loop (interfaces with the manager and tasks) |
| `main.cpp` | entry point driving `app::setup()` and `app::loop()` |
| `sys/**` | the generated context tree + task scaffolds |
| `sys/context.hpp` | `sys::context` — the root that owns every subsystem context |
| `sys/task.hpp` | the task base alias bound to `global::task_id` |
| `config/wiring.hpp` | the task manager (built from the generated per-tier task lists) and channels |
| `hal/` | your hardware drivers, `namespace hal` (see `hal/README.md`); nest freely, include as `"hal/…"` |
| `support/` | your software / linking helpers incl. transports, `namespace support` (see `support/README.md`) |
| `generated/task_id.hpp` | the `global::task_id` enum (rewritten every run) |
| `generated/task_list.hpp` | the per-tier task typelists (rewritten every run) |

Each scope's `context.hpp` holds its own state **and** its child scopes' contexts
as members, so the whole tree is owned by one root object, `sys::context`,
built once, top-down.

Regenerate with:

```
etask generate examples/quadcopter/schema.yaml \
    --out       examples/quadcopter/sys \
    --task-id   examples/quadcopter/generated/task_id.hpp \
    --task-list examples/quadcopter/generated/task_list.hpp
```

## A complete integration

This example shows the **full path** from schema to running flight controller:
schema → generated task tree and context composition → task manager built from
the typelist → app lifecycle coordinating sensor reads, navigation, and thrust
commands. It demonstrates:

- Multi-level nested scopes (`rotors/fl`, `sensors/imu`) with their own contexts.
- Abstract scopes expanded to arrays of concrete subscopes.
- Concurrent tasks with `capacity` bounds across an array.
- Read-only sensor subscopes feeding navigation and safety logic.
- A root-level failsafe task that can reach **all** subsystems through the system
  context to enforce safety constraints.

## Notes on buildability

This is a **near-buildable project** — all architectural pieces are present and
correct. What remains:

- **Task adapter step:** Tasks here have **native-typed constructors**
  (`set_thrust(float level, context&)`), which is the schema generator's design.
  The `task_manager` expects each task to be constructible from a single
  `etools::memory::buffer_view` (for wire payloads). Each task must be wrapped in
  `etask::core::task_unpack_adapter<Task, Args...>` to unpack wire data and bind
  the scope's context. The generated `task_list` will apply this adapter when that
  generator step is complete. See `config/wiring.hpp` for the `@warning` note.

- `on_complete()` on a task with `returns:` fixes the result *shape*; packing the
  actual values is left as a `// TODO` in the task's `.cpp` file.
