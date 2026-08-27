# etask on PlatformIO

A minimal ESP8266 project, and the reference for what etask's PlatformIO
integration does. Four tasks on the on-board LED, one per tier, so the tiers can
be compared side by side in something small enough to read in a sitting.

## Getting it running

```bash
pio run -t etask-generate    # schema.yaml -> src/sys/ + src/generated/
pio run                      # build
pio run -t upload            # flash
```

The first command is needed once, and again after any schema edit. The build
will tell you when.

## Layout

| path | what it is | who owns it |
|------|------------|-------------|
| `schema.yaml` | the task set and wire protocol - the generator's input | you |
| `platformio.ini` | build config; the `extra_scripts` line is the integration | you |
| `src/main.cpp` | Arduino `setup`/`loop`, forwarding to `app::` | you |
| `src/app.{hpp,cpp}` | the application lifecycle | you |
| `src/config/` | the composition root: task manager and channels | you |
| `src/sys/**` | task bodies and scope contexts - **created once, then yours** | you |
| `src/generated/**` | task ids, per-tier task lists, scope accessors | the generator |
| `.schema.uids.json` | the uid ledger - **commit it** | the generator |

Everything lives under `src/`, including `src/generated/`. PlatformIO's `lib/`
would be the tidier home for generated code, but the scope accessors include the
contexts that sit beside the task bodies, and a library under `lib/` cannot reach
back into `src/`.

### The uid ledger

`.schema.uids.json` records which wire uid each task holds, so a task keeps its
id as the schema grows. It is part of the wire contract: lose it and every peer
that knows this board is talking to the wrong tasks. Commit it next to
`schema.yaml`.

## What the build does

On every build the integration checks that `src/generated/` is current with
`schema.yaml`. If it is, nothing happens. If the schema has moved ahead, the
build **fails** and names the command that fixes it.

It does not regenerate on its own, deliberately. A build that rewrites your
source tree as a side effect can clobber an edit you are in the middle of, and it
cannot ask first - there is no terminal to prompt from under CI, in an IDE, or in
a background build. So it stops.

Regenerating only ever rewrites the generated sections. Task bodies, contexts,
and config are created once and then yours; the generator will not touch them,
and when the schema changes in a way that needs a hand edit - a task changing
tier, say - it says so rather than guessing.

## The four tiers, as this example uses them

| task | tier | why |
|------|------|-----|
| `led.on` | `instant_task` | acts on arrival, answers nobody. No vtable, no storage, no tick. |
| `led.off` | `instant_task` | same |
| `led.blink` | `polled_task` | runs across ticks and decides when it has blinked enough |
| `led.read_brightness` | `oneshot_task` | runs once, and the caller wants the answer |

The tier is what a task *is*, and it decides what the task costs. `led.on`
carries no lifecycle at all - its constructor is the whole task - which is why
most of a robot's vocabulary belongs there.

## Requirements

The generator ships inside the etask library, so `lib_deps = MarikTik/etask` is
all that is needed. It parses YAML, and PlatformIO's own Python has no reason to
carry PyYAML - the build says so, with the exact command, the first time:

```
<platformio's python> -m pip install pyyaml
```

That is its only dependency.
