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

Done so far, all on `chore/consistency-pass`:

- ~~**Stale documentation about the heap.**~~ Checked and clean. The library
  headers never carried it - `polled_task_manager.hpp:357` and its stateful twin
  already said "no heap, and no reallocation", and `README.md:614` already
  claimed no heap on a task's path. Only `bench/` was stale, and that was
  corrected with the measurement. One comment in `bench/runtime/src/main.cpp`
  still said `max_task_load`; fixed.
- ~~**`update()`'s budget sensitivity is undocumented.**~~ Both managers'
  `update()` now carry a Cost section with the measured figures, and the
  README's `budget:` entry carries the RAM-per-slot and idle-floor numbers,
  since the schema is where the choice is actually made.
- ~~**`task_limit_reached` vs `task_budget_exhausted`.**~~ Both reachable, both
  covered by `integration/bombardment`. Its README recorded two places where the
  documented meanings did not match behaviour; the behaviour is defensible and
  pinned, so the wording was corrected instead.

Codegen bugs from `project/audit-2026-08.md`, all fixed with regression tests
that fail against the old code (2026-09-01):

- ~~**`rename` rewrote the first textual `Old(`**~~ - a doc example or overload
  above the constructor was renamed instead, leaving the real one stale and the
  header uncompilable. Now anchored on `//! etask:sig`.
- ~~**CRLF churn**~~ - `DocRegion` converted whole files CRLF→LF; `ManagedRegion`
  was worse, leaving *mixed* endings because appended items got no `\r`.
- ~~**`signature_updater` paren counting**~~ - a default argument holding an
  unbalanced literal paren truncated the declaration. Now literal- and
  escape-aware.
- ~~**A schema node named `sys`**~~ - documented rather than rejected: it
  compiles clean (verified), so refusing it would break working schemas. The
  genuinely broken case, a flattened-path uid collision, was already refused.

Still open:

- **Nothing rejects `concurrency` >= its tier's `budget`.** The per-uid check
  runs first, so such a task can never report `task_budget_exhausted` and the
  caller is told to raise a limit that is not binding. Now documented in three
  places, but the generator could simply refuse it.
- **The consistency pass proper has not been done.** The items above were the
  ones the runtime work pointed at; a systematic read for consistent naming,
  error handling and documentation depth across the four libraries has not
  happened. Fixing the two live bugs found on the way (see below) took the
  session's remaining room.

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
- **`packet_size_for` needs regeneration and an on-target check.** The formula is
  tightened (frames shrink up to 8 bytes) and all four mirrors of the arithmetic
  agree, but **no project has been regenerated and nothing has run on hardware**:
  the machine has been under the 4 GB build floor since the change. Before
  trusting it: regenerate every `integration/` project, rebuild, run each
  `verify.py`, and flash `wide_params` or `multi_link` to confirm host and device
  still agree on the wire. This is a wire-format break, so a stale binary paired
  with a fresh one misframes silently.
- **Remaining framework bugs** from an earlier review:
  `internal_channel` ScratchBytes default, `begin_handshake` CRTP.
  - The `ScratchBytes` default of 64 is a guess: a task returning more than that
    packs nothing and only asserts in debug. `external_channel` has a
    `static_assert` against `Link::reply_payload_need` for exactly this, and the
    internal channel has no equivalent because it is not tied to a link. The fix
    is to derive the bound from the manager's task pack rather than defaulting it.
- **Scaffold build ordering.** The schema-drift check runs before the generate
  target, so a first build of `all_tiers` or `deep_tree` fails until
  `-etask-generate` is named explicitly. Note the check also fires on a stale
  *timestamp* alone - a `git checkout` that touches `schema.yaml` is enough -
  and the regeneration it demands then reports "created 0, updated 0", so the
  message overstates what is wrong.
- **`integration/` is not wired into CI.** `.github/workflows/ci.yml` references
  the projects but nothing runs them. All six pass as of 2026-09-01; two of them
  were failing until this pass, and nothing would have caught that.

Closed during the consistency pass (2026-09-01):

- ~~**`oneshot_task` never runs `on_execute`**~~ - **not a bug.** `oneshot_task`
  is `instant_task` with a return value: the work belongs in the **constructor**,
  so the task is finished the moment it exists and `on_execute()` is never
  called by design. The two failing `all_tiers` checks encoded a lifecycle the
  header described but the tier never had. Header and checks corrected; the tier
  is unchanged. `all_tiers` passes 43 of 43.
- ~~**duplicate_task status code**~~ and ~~**concurrency vs budget
  interaction**~~ - resolved in documentation. Both behaviours are defensible
  and pinned by `integration/bombardment`; the wording describing them was
  wrong. See `status_code.hpp` and that project's README.
- ~~**`accept_handshake` undriven**~~ - `many_returns` never completed the
  handshake its generated link requires, so `external_channel::complete()`
  silently dropped all sixteen replies. Fixed in that harness; the underlying
  `begin_handshake` CRTP issue (its preamble frame does not fit `Hub::send`'s
  signature) is why it could not simply call `begin_handshake()`, and remains
  open above.
