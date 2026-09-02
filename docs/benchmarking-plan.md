# Benchmarking plan

The state of the measurement work, and what is left to do. Written as a handoff:
someone picking this up should be able to start from here without reading the
history.

## Where things stand

**Compile-time work is finished** and recorded in
[compile-scaling.md](compile-scaling.md). Four fixes landed, four ideas were
rejected on measurement, and the remaining cost is structural rather than
accidental. Do not re-open it before the runtime work: runtime changes will move
the code that compile time measures, so re-measuring now would be measuring a
moving target.

**Runtime cost has never been measured.** `bench/runtime/` holds a harness with
the right shape - paired comparison of the same work reached through etask and
through a hand-written `switch` - but it has not been run, its numbers have not
been published, and nothing checks it in CI.

## Order of work

1. **Runtime benchmarking** (below). This is the open task.
2. **Code consistency pass** - runtime work will surface rough edges; fix them
   while the context is fresh.
3. **Re-run compile-time benchmarks** last, so the published figures describe the
   code as it finally stands. `scripts/strain.py --resume` re-runs the ladder;
   `bench/strain.jsonl` holds the current points to compare against.

## 1. Runtime benchmarking

### What to measure

The framework's cost, not the work's. Every case is a paired comparison of
identical work reached two ways, and the delta is the only publishable number:

- **Dispatch latency** - uid arrives, task starts. The `dispatch_factory` path
  against a hand-written `switch`. Expect this to be the headline figure.
- **Per-tick overhead** - `manager.update()` with N registered tasks, none
  runnable, against an empty loop. This is what a device pays continuously.
- **Registration and teardown** - `register_task` through to `complete_task`,
  including the slot scan and handle destruction.
- **The wire path** - `external_channel` from frame arrival to task start:
  checksum, `carries()`, unpack, dispatch. Against a hand-rolled parser.
- **Scaling** - each of the above at several task counts. The compile-time work
  found a step change at 256 tasks (uid width, LLUT to FKS backend); whether
  that shows at runtime is unknown and worth knowing.

### How to measure it

- **On the ESP32**, not the host. `esp_timer_get_time()` gives microseconds;
  `xthal_get_ccount()` gives cycles and is what a dispatch measurement needs.
- **Paired, interleaved, many repetitions.** Alternate raw and task within one
  run so drift affects both equally.
- Report **median and a spread**, never a bare mean - one flash-cache miss
  distorts an average.
- Pin what varies: CPU frequency, cache configuration, whether the code runs from
  IRAM or flash. State all of it.
- Watch for the compiler defeating the benchmark: a task whose result is unused
  can be optimised away entirely. Consume results through a `volatile`.

### Deliverable

A results document with tables and graphs, stating **units on every axis**, the
hardware, the toolchain, the build flags and the conditions. The tables in
compile-scaling.md are the format to match. Publish the paired delta, and the
absolute numbers behind it so a reader can check the arithmetic.

### Conventions

Two rules, both learned the hard way in the compile-time work.

**Log to a file as each run finishes, never at the end of a session.** A long
run that is interrupted must keep every point it already measured.
`scripts/strain.py` does this - one JSON object appended per point, with
`--resume` to skip what is already recorded - and a runtime harness should do
the same. Results held only in a terminal scrollback or a session's memory are
lost the moment anything goes wrong, and re-measuring hours of work to recover a
number nobody wrote down is the most avoidable kind of waste.

**Record the assumptions beside the numbers.** Not just the hardware and flags,
but the conditions the run depended on: what else was running, whether the board
was freshly reset, what the harness pinned and what it left free, and anything
that was measured indirectly rather than observed. A number without its
assumptions cannot be compared against a later one.

**Time budget.** A run may take up to two hours. Memory, not duration, is the
constraint on this machine: stay inside roughly 2 GB per process and a long run
is fine. See the build safety section - the ceilings are enforced, not advisory.

## 2. Consistency pass

Not yet scoped. The intent is that the code read as one library rather than four:
consistent naming, consistent error handling, consistent documentation depth. Do
this after runtime work, so it is informed by what that work exposes.

## Hardware and toolchain

Everything measured so far, and everything the runtime work will use:

| | |
|---|---|
| Host CPU | Intel Core i7-9700, 8 cores / 8 threads, 3.00 GHz base, 4.70 GHz max |
| Host RAM | 15 GB, of which roughly 5 GB is free with an editor and browser resident |
| Host OS | Linux 7.0.0-30-generic |
| Host compilers | GCC 15.2.0, Clang 21.1.8 |
| Target | ESP32-D0WD (Xtensa LX6), `esp32dev`, 1,310,720 B flash, 327,680 B RAM |
| Target toolchain | xtensa-esp32-elf-g++ 8.4.0 (crosstool-NG esp-2021r2-patch5) |
| Target flags | `-Os -ggdb -fno-rtti -ffunction-sections -fdata-sections`, `-Wl,--gc-sections` |
| Board connection | `/dev/ttyUSB0`, CP210x UART bridge, 115200 baud |

**The board is physically attached**, so runtime measurement needs no
substitute. It may not always be: a runtime harness should fail loudly when the
port is absent rather than silently reporting nothing.

## Build safety

Non-negotiable, and enforced. See the ceilings in `CLAUDE.md` and the PreToolUse
hook at `.claude/guard_build.py`, which blocks violations before they run.

- `pio run` is always `-j 1`, one build at a time, never above ~600 tasks.
- `cmake --build` gets `-j 2`.
- Nothing starts below 4 GB free.
- Large host probes run under `ulimit -v` so an over-run fails cleanly.

This machine's editor has been killed three times by builds. The hook exists
because prose alone did not prevent the third.

## Open work unrelated to benchmarking

Carried forward so it is not lost:

- **etools is on an unmerged branch.** `assert-flash-footprint` holds four
  commits that etask on `main` now depends on: `f9619f7`, `f05bc64`, `ea62c95`,
  `ca8a993`, `1d6c57b`, `fbe56d8`. Merge it.
- **Nothing is pushed.** Both repositories are ahead of their remotes.
- **`oneshot_task` never runs `on_execute`.** A real framework bug, caught by
  `integration/all_tiers` (41 of 43 checks) and deliberately left failing.
- **Seven other framework bugs** from an earlier review remain unfixed:
  duplicate_task status code, concurrency vs budget interaction,
  `internal_channel` ScratchBytes default, `begin_handshake` CRTP,
  `accept_handshake` undriven, `packet_size_for` over-rounding.
- **Scaffold build ordering.** The schema-drift check runs before the generate
  target, so a first build of `all_tiers` or `deep_tree` fails until
  `-etask-generate` is named explicitly.
- **`integration/` is not wired into CI.** `.github/workflows/ci.yml` references
  the projects but nothing runs them.
