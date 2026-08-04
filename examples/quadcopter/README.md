# quadcopter — a second worked etask example

A quadcopter flight controller, generated from one schema. It is deliberately a
different *shape* from the [humanoid](../humanoid/) example: there the tree is
limb-pairs (arms/legs); here it is a rotor **array** feeding a controller, a
read-only sensor suite, and a navigation layer that commands them.

## The machine

- `rotors` → `rotor` *(abstract, expanded to `fl`/`fr`/`rl`/`rr`)* → `set_thrust`
  (all four spin together → `capacity<…, 4>`), `stop`.
- `sensors` → `imu` → `read` (six axes), `baro` → `read_altitude`,
  `gps` → `fix` (positional returns: `lat, lon, sats`).
- `nav` → `fly_to`, `hold`, `land`.
- `failsafe` — a root-level task (uid 255). It receives `system::context` and,
  through it, reaches **every** rotor to cut thrust. That is the whole reason a
  system-level task is handed the composition root rather than one subsystem.

## Layout

| path | what it is |
|------|------------|
| `schema.yaml` | the input — the whole craft in one file |
| `system/**` | the generate-once task scaffolds + the `context` composition tree |
| `system/context.hpp` | `system::context` — the root that owns every subsystem context |
| `generated/task_id.hpp` | the `global::task_id` enum (rewritten every run) |
| `generated/task_list.hpp` | the `generated::task_list` typelist (rewritten every run) |

Each scope's `context.hpp` holds its own state **and** its child scopes' contexts
as members, so the whole tree is owned by one root object, `system::context`,
built once, top-down.

Regenerate with:

```
etask-gen generate examples/quadcopter/schema.yaml \
    --out       examples/quadcopter/system \
    --task-id   examples/quadcopter/generated/task_id.hpp \
    --task-list examples/quadcopter/generated/task_list.hpp
```

## Reading it, not building it

This is **illustrative output**, not a buildable project — that is the
`template/` scaffold's job (task base, transport, wiring, `main`). The task files
reference `task.hpp` (the `using task = …` alias) and `global::task_id`, which a
real project supplies; the example ships neither. Tasks have **native-typed
constructors** (`set_thrust(float level, context&)`), and `on_complete()` on a
task with `returns:` fixes the result *shape* — packing the actual values is left
as a `// TODO`.
