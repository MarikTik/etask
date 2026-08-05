# humanoid — a worked etask example

A small humanoid robot, used to show the full output of the schema generator on
a realistic tree. This is a **complete, near-buildable project**: the schema, the
task scaffolds it produces, the context tree, the wiring, and the app lifecycle
are all here. The single remaining step (wrapping generated tasks in the payload
adapter) is documented in the code.

## The robot

- `head` → `imu` → `read` — sample the accelerometer (returns `ax, ay, az`).
- `arms` → `arm` *(abstract, expanded to `left`/`right`)* → `move_to` (concurrent,
  `capacity<…, 2>`), `stop`, `grasp`.
- `legs` → `leg` *(abstract, expanded to `left`/`right`)* → `step`, `stop`.
- `reboot` — a root-level task with an explicit uid (255). It receives
  `sys::context&` — the composition root — so it can reach every subsystem.

## Layout

| path | what it is |
|------|------------|
| `schema.yaml` | the input — the whole robot in one file |
| `app.{hpp,cpp}` | the robot's setup and loop (interfaces with the manager and tasks) |
| `main.cpp` | entry point driving `app::setup()` and `app::loop()` |
| `sys/**` | the generated context tree + task scaffolds |
| `sys/context.hpp` | `sys::context` — the root that owns every subsystem context |
| `sys/task.hpp` | the task base alias bound to `global::task_id` |
| `config/wiring.hpp` | the task manager (built from `generated::task_list`) and channels |
| `hal/` | your hardware drivers, `namespace hal` (see `hal/README.md`); nest freely, include as `"hal/…"` |
| `support/` | your software / linking helpers incl. transports, `namespace support` (see `support/README.md`) |
| `generated/task_id.hpp` | the `global::task_id` enum (rewritten every run) |
| `generated/task_list.hpp` | the `generated::task_list` typelist (rewritten every run) |

The task tree lives in `sys/` (namespace `sys`): a task's directory becomes its
scope, and every scope carries a `context.hpp`. Each scope's context holds its own
state **and** its child scopes' contexts as members, so the whole tree is owned by
one root object, `sys::context`, built once, top-down.

Regenerate with:

```
PYTHONPATH=tools/src python -m schemav2.cli generate examples/humanoid/schema.yaml \
    --out       examples/humanoid/sys \
    --task-id   examples/humanoid/generated/task_id.hpp \
    --task-list examples/humanoid/generated/task_list.hpp
```

## A complete integration

This example shows the **full path** from schema to running app: schema → generated
task tree and context composition → task manager built from the typelist → app
lifecycle interfacing with the manager. It demonstrates:

- Multi-level nested scopes (`arms/left`, `legs/right`) with their own contexts.
- Abstract scopes expanded to concrete subscopes.
- Concurrent tasks with `capacity` bounds.
- Tasks with parameters and return values.
- A root-level task receiving the system-wide context to coordinate subsystems.

## Notes on buildability

This is a **near-buildable project** — all architectural pieces are present and
correct. What remains:

- **Task adapter step:** Tasks here have **native-typed constructors**
  (`move_to(float x, float y, context&)`), which is the schema generator's design.
  The `task_manager` expects each task to be constructible from a single
  `etools::memory::buffer_view` (for wire payloads). Each task must be wrapped in
  `etask::core::task_unpack_adapter<Task, Args...>` to unpack wire data and bind
  the scope's context. The generated `task_list` will apply this adapter when that
  generator step is complete. See `config/wiring.hpp` for the `@warning` note.

- `on_complete()` on a task with `returns:` fixes the result *shape*; packing the
  actual values is left as a `// TODO` in the task's `.cpp` file.
