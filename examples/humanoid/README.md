# humanoid — a worked etask example

A small humanoid robot, used to show the full output of the schema generator on
a realistic tree. This directory is self-contained: the schema, the task
scaffolds it produces, and the always-regenerated artifacts.

## The robot

- `head` → `imu` → `read` — sample the accelerometer (returns `ax, ay, az`).
- `arms` → `arm` *(abstract, expanded to `left`/`right`)* → `move_to` (concurrent,
  `capacity<…, 2>`), `stop`, `grasp`.
- `legs` → `leg` *(abstract, expanded to `left`/`right`)* → `step`, `stop`.
- `reboot` — a root-level task with an explicit uid (255). It receives
  `system::context&` — the composition root — so it can reach every subsystem.

## Layout

| path | what it is |
|------|------------|
| `schema.yaml` | the input — the whole robot in one file |
| `system/**` | the generate-once task scaffolds + the `context` composition tree |
| `system/context.hpp` | `system::context` — the root that owns every subsystem context |
| `generated/task_id.hpp` | the `global::task_id` enum (rewritten every run) |
| `generated/task_list.hpp` | the `generated::task_list` typelist (rewritten every run) |

The top of the tree is `system/` (namespace `system`): a task's directory
becomes its scope, and every scope carries a `context.hpp`. Each scope's context
holds its own state **and** its child scopes' contexts as members, so the whole
tree is owned by one root object, `system::context`, built once, top-down.

Regenerate with:

```
etask-gen generate examples/humanoid/schema.yaml \
    --out       examples/humanoid/system \
    --task-id   examples/humanoid/generated/task_id.hpp \
    --task-list examples/humanoid/generated/task_list.hpp
```

## Reading it, not building it

This is **illustrative output**, not a buildable project — that is the `template/`
scaffold's job (task base, transport, wiring, `main`). Notes while reviewing:

- Task files reference `task.hpp` (the `using task = …` alias) and `global::task_id`,
  which a real project supplies; the example ships neither.
- Tasks have **native-typed constructors** (`move_to(float x, …, context&)`), and
  each scope's `context.hpp` composes its children into the `system::context`
  tree. The generated `task_list` lists the tasks bare today; wrapping each in
  `etask::core::task_unpack_adapter` / `scoped_task_unpack_adapter` (so the
  manager can build them from a wire payload, binding the scope's context) is the
  remaining generator step.
- `on_complete()` on a task with `returns:` fixes the result *shape*; packing the
  actual values is left as a `// TODO`.
