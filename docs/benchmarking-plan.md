# Benchmarking plan

The state of the measurement work, and what is left to do. Written as a handoff:
someone picking this up should be able to start from here without reading the
history.

## Where things stand

**Compile-time work is finished** and recorded in
[compile-scaling.md](compile-scaling.md). Four fixes landed, four ideas were
rejected on measurement, and the remaining cost is structural rather than
accidental. It is still not time to re-open it: the consistency pass will move
the code that compile time measures, so re-measuring before that lands would be
measuring a moving target. Step 3 below is where it comes back.

**Runtime cost is measured** (2026-09-01) and published in
[../bench/RESULTS.md](../bench/RESULTS.md) §3, §4 and §6, with raw captures in
`bench/data/`. Headline figures, all on an ESP32-D0WD-V3 at 240 MHz, `-O2`:

| | |
|---|---|
| Instant dispatch vs a hand-written fn-ptr call | **+97 ns**, flat across a 95× workload range |
| Polled `update()` tick vs a raw loop | **+616 ns**, flat |
| Stateful vs polled tick (suspendability) | **+43 ns** |
| `update()` scaling | **exactly O(n)**: 541.6 ns/task, linear to within 2 ns over 0→32 |
| Idle floor (0 live tasks) | **127 ns** |
| Heap | **zero allocations**, construction through teardown |
| RAM | ≈36 B per concurrent slot, 348 B per manager |

The relative figure depends entirely on the work being wrapped: 7.7× on a task
that does one store, 1.08× on one doing ~500 flops. Both are in the document;
neither alone is honest.

## Order of work

1. ~~**Runtime benchmarking**~~ - done, see above.
2. **Code consistency pass** - **this is the open task.** Runtime work surfaced
   rough edges; fix them while the context is fresh. See below.
3. **Re-run compile-time benchmarks** last, so the published figures describe the
   code as it finally stands. `scripts/strain.py --resume` re-runs the ladder;
   `bench/strain.jsonl` holds the current points to compare against.

Two headless benchmark tracks also remain unrun, and are independent of the
above: the **static footprint** ladder (§2, which the flash budget in §6 is
blocked on) and the **WiFi round trip** (§5, which needs a network as well as a
board).

## 1. Runtime benchmarking — DONE

Kept below as the record of what was asked for and what it turned into. Three
things were learned that the brief did not anticipate:

**The heap track's premise had expired.** It was written to measure a
`std::vector` design and to provide a before/after against the pending
`static_vector` fix. That fix had already landed, so the old `heap.cpp` did not
even compile — `max_task_load` is now a compile-time template parameter and the
constructor takes no arguments. Rewritten around the current design; the result
is a stronger claim (etask allocates *nothing*) and no before/after is available
without reverting etools.

**A paired comparison needs matched budgets, not just matched work.** The
stateful-vs-polled case briefly reported the stateful tier as 8 ns *faster* than
polled, which cannot be true of a tier doing strictly more work. Cause: the
tick-scaling sweep's `capacity<scale_case, 32>` had been added to the shared
manager, so the polled tier carried a 38-slot budget against stateful's 3, and
part of `update()`'s cost tracks the budget. Fixed by giving the sweep its own
manager. Recorded in RESULTS.md §3c rather than quietly corrected.

**An unused budget is not free.** `update()` resets a `std::bitset<Budget>` and
sweeps the erase range every tick, so the idle floor is paid per *declared* slot,
not per live task: 113 ns at budget 1, 325 ns at budget 128. Sub-linear and
cheap, but not zero — and worth knowing before declaring a generous
`capacity<T, N>`. This became its own case (§3e).

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

## 2. Consistency pass — the open task

The intent is that the code read as one library rather than four: consistent
naming, consistent error handling, consistent documentation depth.

What the runtime work exposed, as a starting list rather than a complete scope:

- **Stale documentation about the heap.** `bench/` has been corrected, but the
  `std::vector` / `max_task_load` design is likely described elsewhere in prose
  and doc comments. `max_task_load` is now a template parameter named `Budget`;
  anything still calling it a constructor argument is wrong. Grep for
  `max_task_load`, `std::vector`, `reserve` and `reallocat` across docs and
  headers.
- **`update()`'s budget sensitivity is undocumented.** Neither manager's doc
  comment mentions that per-tick cost scales with the declared budget as well as
  the live count. Users choosing a `capacity<T, N>` deserve to know.
- **`task_limit_reached` vs `task_budget_exhausted`.** Both exist and mean
  different things (`status_code.hpp:55,61`). Worth checking that both are
  actually reachable and that the distinction is documented where a user meets
  it, not only at the enum.
- The bug list below is separate from consistency, but overlaps it — several of
  those are error-handling inconsistencies rather than logic errors.

## Hardware and toolchain

Everything measured so far, and everything the runtime work will use:

| | |
|---|---|
| Host CPU | Intel Core i7-9700, 8 cores / 8 threads, 3.00 GHz base, 4.70 GHz max |
| Host RAM | 15 GB, of which roughly 5 GB is free with an editor and browser resident |
| Host OS | Linux 7.0.0-30-generic |
| Host compilers | GCC 15.2.0, Clang 21.1.8 |
| Target | **ESP32-D0WD-V3 rev 3.1** (Xtensa LX6, dual core, 240 MHz), `esp32dev`, 1,310,720 B flash, 327,680 B RAM, MAC `d8:bc:38:f9:45:b8` |
| Target toolchain | xtensa-esp32-elf-g++ 8.4.0 (crosstool-NG esp-2021r2-patch5) |
| Target flags | `-Os -ggdb -fno-rtti -ffunction-sections -fdata-sections`, `-Wl,--gc-sections` |
| Runtime bench flags | `-std=gnu++17 -O2 -DNDEBUG` — speed, not size, is what that track measures |
| Board connection | `/dev/ttyUSB0`, CP210x UART bridge, 115200 baud |

**The board is physically attached** and is a **test board** — its contents are
expendable, so no permission is needed before flashing. Identify the chip first
regardless (`esptool.py chip_id`): boards are swapped by hand and an ESP32-S3
presents the same USB descriptor as a classic ESP32.

The port is a single exclusive resource. When more than one agent might drive
it, they must agree whose turn it is before one opens it.

A runtime harness must fail loudly when the port is absent rather than silently
reporting nothing — `bench/scripts/read_serial.py` does, and also logs each line
as it arrives so an interrupted capture keeps what it had.

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

- **etask is not pushed.** etools is released as `v1.3.0` and pushed; etask's
  `main` is ahead of its remote and etask now requires that tag.
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
