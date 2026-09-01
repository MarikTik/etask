# deep_tree — an integration test for the schema's structural machinery

Not an example of a device. `examples/quadcopter` and `examples/humanoid` show
what a real schema looks like; this project exists to be **hard in the specific
ways the generator's four passes can go wrong**, and to check the result with
assertions rather than by eye.

One schema, 294 tasks, five levels of scope, three stacked abstract scopes, a
two-byte uid space, and a host-side driver that proves every one of those tasks
is a genuinely separate thing.

```bash
cmake -S . -B build && cmake --build build   # ~13 s, 294 translation units
./verify.py                                   # 7 checks, exits non-zero on failure
```

## What it is trying to break

| feature | how this schema stresses it |
|---|---|
| deep nesting | `mesh.<segment>.<node>.<probe>.<task>` — five scope levels, each with its own namespace, directory, `context` member, and `../` depth in its includes |
| nested abstract scopes | `probe` is abstract inside `node`, which is abstract inside `segment`. `Tree.__copy_node` preserves `kind`, so a clone stays abstract and is expanded on the next recursion — three stacked levels is where getting that wrong shows up |
| abstract expansion | 6 × 4 × 3 = 72 leaf scopes from one definition, 4 tasks each |
| uid width | 294 tasks is past the 256 a one-byte uid holds, **and** `bus.reserve.emergency_halt` pins 40000 — the two independent reasons `__uid_width` must pick 2 |
| explicit vs derived | the mesh is entirely derived; `bus.reserve` mixes pins (40000, 300) among derived siblings, so the collision probe in `__generate_uid` has to walk around them |
| flattened names | `bus.link_state.probe` and `bus.link.state_probe2` are one component boundary apart — both fold to nearly the same C++ enumerator and Python class |
| the context tree | 73 contexts composed into one `sys::context`, reached through `generated/scopes.hpp` |
| the uid ledger | four separate checks in `verify.py`, described below |
| all four tiers | every leaf scope carries a oneshot, a polled, a stateful, and an instant task, so each of the three managers sees 72+ distinct uids |

## Layout

| path | what it is | who owns it |
|---|---|---|
| `schema.yaml` | the input — every structural stressor, with the reason for each written beside it | you |
| `verify.py` | the host driver and every assertion | you |
| `fill_bodies.py` | writes the one-line identifying body into each scaffolded task | you |
| `src/main.cpp` | the host entry point: uids in on stdin, identities out on stdout | you |
| `src/board_main.cpp` | the Arduino entry point, forwarding to `app::` | you |
| `src/app.{hpp,cpp}` | the board lifecycle: walks a sample of the tree over Serial | you |
| `src/support/witness.{hpp,cpp}` | the log each task reports itself to | you |
| `src/support/exercise.{hpp,cpp}` | starts one task by raw uid and reports what ran | you |
| `src/config/wiring.hpp` | the manager and channels, built from the generated lists | you |
| `src/sys/**` | 294 task bodies and 73 contexts — **created once, then yours** | you |
| `src/generated/**` | task ids, per-tier task lists, scope accessors, link packets | the generator |
| `python/tasks.py` | the client bindings — a second, independent projection of the schema | the generator |
| `.schema.uids.json` | the uid ledger — **the thing most of this project is about** | the generator |

## How a task proves which task it is

Every task's body is the same one line: report the uid it was **compiled** with.

```cpp
const auto self = static_cast<std::uint16_t>(uid);
support::witness::record(self, support::phase::completed);
return {self};
```

Identical source in all 294, which is the point — if two of them are the same
task under two numbers, identical bodies will say so. `uid` is
`global::task_id::<dotted path>`, fixed at compile time from the schema path, so
a task running under another's registration reports the other's number.

The driver starts tasks by **raw uid**, never by name. Naming a task in C++ would
only assert that the compiler can tell 294 classes apart, which was never in
doubt; feeding an opaque `std::uint16_t` to `register_task` asks the question
that matters, which is whether the *registries* can.

Results reach the host through the witness rather than through the ordinary
result path, because two of the three cases cannot travel it: `internal_channel`
runs `on_complete` against a discard scratch and drops the result, and an
`instant_task` (72 of these tasks) has no `on_complete` at all.

## The checks

```
ok    structure: 294 tasks, distinct uids, 2-byte width, fan-out complete
ok    identity: all 294 tasks reachable by uid, each answering as itself
ok    abstract scopes: 72 instances per definition, each a genuinely separate task
ok    deep paths: the generated client agrees with the ledger
ok    the ledger: no uid moved across a no-op regeneration, nor when a task was added
ok    the ledger: a removed task's uid stays reserved, and nothing else moved
ok    the ledger: crossing the one-byte uid boundary renumbers nothing
```

The last three are the reason this project exists. A uid is a wire identifier: a
peer built last month puts it in a request and matches it in a reply. If a uid
moves because somebody edited the schema, every deployed peer is quietly
addressing the wrong task — the frames still parse, the checksums still pass,
and the device does the wrong thing.

The boundary check is the sharpest of them, and it builds its own throwaway
schema to run: **250 tasks, then 300**. Before the ledger, a derived uid was a
hash folded into a width chosen from the task *count*, so the 257th task
re-derived every id in the project at a wider digest. The check confirms both
halves — that with a ledger nothing moves, and that with `--no-uid-ledger` on the
same two schemas the uid *does* move (measured: `s.t0` goes 203 → 16517). Without
that second half the first would be passing for free.

Every ledger check works on a copy in a temporary directory, so running
`verify.py` never touches the real `.schema.uids.json`.

## Building for a board

```bash
pio run -e esp32dev
```

**The full tree does not fit an ESP32, and the number it misses by is the useful
result.** It compiles for xtensa; it fails to link, with rodata over the 4 MB
`drom0_0_seg` region by 163,240 bytes. No partition table or flash size changes
that — the same overflow appears with the stock 1.25 MB table, with
`huge_app.csv`'s 3 MB, and with a hand-written 6 MB one.

Measured, varying only the mesh's segment count:

| segments | tasks | flash | per task | RAM |
|---|---|---|---|---|
| 2 | 102 | 0.91 MB | 9.4 KB | 26.6 KB |
| 4 | 198 | 2.37 MB | 12.6 KB | 27.2 KB |
| 5 | 246 | 3.42 MB | 14.6 KB | 27.5 KB |
| 6 | 294 | — | — | link fails |

Two conclusions worth carrying elsewhere. **Flash grows faster than the task
count** — per-task cost climbs from 9.4 KB to 14.6 KB across that range, so a
device sized by extrapolating from a small prototype will be sized wrong.
**RAM barely moves**: 26.6 → 27.5 KB across 144 extra tasks, because `budget:`
sizes the managers' inline storage by concurrent tasks rather than by task
*types*. A tree this size is a flash problem and very nearly not a RAM one.

This env is left pointing at the full schema on purpose. Shrinking it so the
build goes green would trade away the >256 tasks the uid-width test needs. To
build something that flashes: set the mesh's `segment` instances to five,
regenerate, delete the orphaned `src/sys/mesh/s5/`, and use
`partitions_deep_tree.csv` — verified at 3.42 MB flash, 8.4% RAM.

`esp32` rather than `esp8266` throughout: 294 tasks across three managers is a
different order of thing from four tasks on an LED, and a size failure on an
ESP8266 would say more about the board than about the generator.

## Notes for whoever reads this next

Three things this project turned up that are not about deep_tree itself:

1. **A flattened-name collision is caught only when `--python` is passed.**
   `PythonFile.__reject_class_name_collisions` rejects `a_b.c` against `a.b_c`,
   but nothing checks the C++ side. Generating those two without `--python`
   emits a `global::task_id` with the enumerator `a_b_c` defined twice, which is
   a hard compile error some distance from its cause. That is why the near miss
   in this schema is spelled `state_probe2` — the real collision cannot live in
   a project that has to build.

2. **The collision is reported as an uncaught `ValueError` traceback**, not as
   one of the generator's own error types with a schema path.

3. **Schema `params` are not marked `[[maybe_unused]]` in the scaffold**, though
   the `context&` is. Every generated task with a parameter it does not yet use
   warns under `-Wunused-parameter` — 72 warnings here, all of them noise around
   a `// TODO` the generator itself wrote.
