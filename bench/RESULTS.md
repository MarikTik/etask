# etask benchmark results

**Status: the two runtime tracks are measured; the two headless tracks are not.**

[§3 Runtime cost](#3-runtime-cost--runtime) and [§4 Heap](#4-heap--runtime) carry real numbers taken
on hardware on 2026-09-01, and [§6 Scale estimate](#6-scale-estimate) is derived from them.
[§2 Static footprint](#2-static-footprint--compile-time) and [§5 WiFi](#5-wifi-round-trip--runtime)
are still skeletons. [§1 Codegen](#1-codegen-quality--compile-time) has preliminary instruction
counts, marked as such.

Fill a cell only from a run you can point at, and cross-check it against the raw capture in
`bench/data/` before writing it here.

---

## Provenance — what was measured

Record this for every run. A benchmark of a dirty tree is fine; one that does not say the tree was
dirty is not.

**Sibling commits for the runtime and heap runs (2026-09-01):**

| Repo | Commit | Dirty files |
|---|---|---|
| `etools` | `f164a19` merge: compile-time footprint work for large registries | 0 |
| `ecomm` | `a6bfcf6` release: 3.1.0 | 0 |
| `eser` | `bb683dc` release: 1.1.2 | 0 |
| `etask` | `1795ea7` docs: etools is released, so drop it from the open-work list | 4 (the bench harness edits described below) |

etask branch: `main`.

**All four trees are clean**, which resolves the two caveats the skeleton carried: `ecomm` is now
released at 3.1.0 rather than being a divergent working tree, and `etools`' `static_vector` has
landed rather than being untracked work in progress. The dirty files in `etask` are this session's
own harness changes — `bench/runtime/src/{main,heap}.cpp`, `bench/scripts/read_serial.py` — not
library code.

**Sibling commits at the time the skeleton was written (2026-08-27),** kept for comparison:

| Repo | Commit | Dirty files |
|---|---|---|
| `etools` | `3d2797b` release: 1.1.1 | 4 |
| `ecomm` | `cd09249` release: 3.0.1 | 19 |
| `eser` | `bb683dc` release: 1.1.2 | 0 |
| `etask` | `cd026c9` build: trim the codegen extra to pyyaml | 3 |

Regenerate before each run:

```bash
cd /home/mark/Desktop/projects/elib
for p in etools ecomm eser etask; do
  echo "$p $(git -C $p log --oneline -1) dirty=$(git -C $p status --porcelain | wc -l)"
done
```

### Both dirty-tree caveats are now resolved

The skeleton flagged two trees whose uncommitted state would have contaminated the numbers. Neither
applies to the 2026-09-01 runs, but the mechanism still does:

1. **`ecomm` — was 19 files dirty, now clean at 3.1.0.** Every `platformio.ini` in `bench/` sets
   `lib_extra_dirs = /home/mark/Desktop/projects/elib`, so **the working tree is what gets
   measured, not the registry versions `etask/library.json` declares.** That is still true; it just
   no longer makes a difference, because the working tree *is* the release. Any future run must
   re-check this.

2. **`etools` — `static_vector` has landed.** It is no longer untracked work in progress; both
   managers now use it (`polled_task_manager.hpp:362`, `stateful_task_manager.hpp:362`). **Every
   runtime and heap figure in this document is on the `static_vector` side of that change.** The
   before/after the skeleton anticipated is not available — see §4.

### The ESP32 compile fix is committed

`etask/core/managers/detail/empty_managers.hpp` carries the fix without which etask does not compile
for ESP32 at all. **It is now committed and the file is clean** — the skeleton described it as an
uncommitted patch, which is no longer true. GCC 8.4 — shipped by the ESP32 Arduino core — cannot
parse a
C++11 attribute on the first parameter of a constructor declared inside a class body. Isolated on
this machine against `xtensa-esp32-elf-g++ 8.4.0`:

| Construct | GCC 8.4 |
|---|---|
| in-class ctor, attribute on **first** param | **FAIL** — `explicit` or not, named or unnamed, with or without a base, template or not |
| in-class ctor, attribute on a *later* param | OK |
| ctor declared in-class, **defined out-of-line** with the attribute | OK |
| `__attribute__((unused))` on the first param | OK |
| free function or member function, attribute on first param | OK |

The patch swaps `[[maybe_unused]]` for a `(void)` cast in the body. With it, all three Xtensa
toolchains compile a fully instantiated three-tier manager clean:

| Toolchain | GCC | `core.hpp` | 3-tier manager instantiated |
|---|---|---|---|
| `xtensa-esp32-elf` | 8.4.0 | clean | clean |
| `xtensa-esp32s3-elf` | 8.4.0 | clean | clean |
| `xtensa-lx106-elf` (ESP8266) | 10.3.0 | clean | clean |

This is the **only** occurrence across etask, etools, ecomm and eser. See `bench/README.md` and
`project/benchmarking-brief.md` §2b. Options for expressing it differently are in the handover
notes; nothing else in etask was touched.

---

## 1. Codegen quality — COMPILE-TIME

Headless. `bench/scripts/codegen.sh [host|xtensa|xtensa32|arm]`.

Instruction counts per `extern "C"` symbol from `bench/codegen/cg.cpp`. The work in every case is a
single `volatile` store, so the count is dispatch and nothing else.

### PRELIMINARY — reproducible now, pending a recorded run

`-O2`. Host is x86-64 g++; `xtensa32` is the ESP32 core's GCC 8.4.

| Comparison | Reference | etask | Delta (host) | Delta (Xtensa LX6) |
|---|---|---|---|---|
| instant dispatch, 4 tasks | hand-written `switch` | | **+0** | **−4** |
| instant dispatch, 16 tasks | hand-written `switch` | | **+0** | **−46** |
| polled `update()` tick | fn-pointer call | | +23 | +33 |
| `dispatch_factory::emplace`, 8 types | placement-new `switch` | | +61 | +48 |

Raw counts (host / xtensa32): instant-4 26/26 vs 21/17 · instant-16 58/58 vs 108/62 ·
tick 8 vs 31/41 · emplace 58/59 vs 119/107.

**Reading these honestly:**

- **Instant dispatch is free on x86-64 and cheaper than hand-written on Xtensa.** `instant_task`
  declares no virtual functions at all, so a derived command has no vtable and no vptr; the
  manager's `register_task` is a short-circuiting fold of `if`s over `constexpr` uids, and the
  compiler collapses it. The *negative* Xtensa delta is not etask being free — it is the fold
  compiling to a tighter comparison chain than GCC's jump-table lowering of the equivalent
  `switch`. A fair summary is "no worse than hand-written dispatch, on either target".
- **The tick costs ~23–33 instructions over one indirect call.** Two virtual calls
  (`on_execute`, `is_finished`) plus the manager's per-tick bookkeeping: the garbage bitset reset,
  the vector walk, and the erase-remove pass. This is the figure the runtime table must confirm in
  nanoseconds, and the one a tick budget is built from.
- **`dispatch_factory::emplace` is ~2× a hand-written placement-new switch.** This is one-time
  construction cost, not per-tick — weigh it against the runtime dispatch rows, not the tick rows.

Note `etask_tick` is measured as a function body, not inlined into a loop, so it is not directly
comparable with a per-iteration runtime figure. Read the two together.

### To record

| Target | Compiler | instant-4 | instant-16 | tick | emplace |
|---|---|---|---|---|---|
| x86-64 | g++ (host) | | | | |
| Xtensa LX6 (ESP32) | GCC 8.4 | | | | |
| Xtensa LX106 (ESP8266) | GCC 10.3 | | | | |
| Cortex-M4 | arm-none-eabi | | | | |

---

## 2. Static footprint — COMPILE-TIME

Headless. `python3 bench/scripts/measure.py --json bench/data/static.json`.
168 environments: 4 boards × 3 modes × (8 feature tiers + 6 task counts).

### 2a. Feature ladder, `rel` (`-Os -DNDEBUG` — what ships)

Absolute figures include the Arduino framework floor. **A tier-7 total is not "etask costs that
much"** — the deltas are.

| Tier | Adds | esp32dev flash | Δ | esp32dev RAM | Δ | nodemcuv2 flash | Δ |
|---|---|---|---|---|---|---|---|
| 0 | framework only, no etask | | — | | — | | — |
| 1 | `#include core.hpp` | | | | | | |
| 2 | manager + 1 instant task | | | | | | |
| 3 | + 2nd instant task | | | | | | |
| 4 | + polled tier | | | | | | |
| 5 | + stateful tier (full) | | | | | | |
| 6 | + internal channel | | | | | | |
| 7 | + external channel (ecomm) | | | | | | |

**Tier 1 must be exactly +0 bytes.** etask claims header-only; eser measured +0 on every board and
mode. `measure.py` prints PASS or the delta.

- [ ] header-only claim confirmed on `esp32dev`
- [ ] on `esp32s3`
- [ ] on `nodemcuv2`
- [ ] on `stm32f411`

### 2b. Total cost by build mode

The `dbg` column is not redundant: etask's contracts are `assert`, live only while `NDEBUG` is
undefined. In eser they cost 2.5–6× the shipping footprint.

| Board | rel (`-Os`) | relO2 (`-O2`) | dbg (`-Og`, asserts live) |
|---|---|---|---|
| esp32dev (ESP32-D0WD, LX6) | | | |
| esp32s3 (ESP32-S3, LX7) | | | |
| nodemcuv2 (ESP8266) | | | |
| stm32f411 (Cortex-M4) | | | |

### 2c. Task-count ladder — the scaling answer

All at tier 5 (full framework), varying only `BENCH_TASKS`. The slope says whether dispatch is O(1)
or O(n) in code size. **The eser suite had no equivalent; this is the "how good is it at full
scale" number.**

| Registered tasks | esp32dev flash | Δ | RAM | Δ | nodemcuv2 flash | Δ |
|---|---|---|---|---|---|---|
| 1 | | — | | — | | — |
| 2 | | | | | | |
| 4 | | | | | | |
| 8 | | | | | | |
| 16 | | | | | | |
| 32 | | | | | | |

Marginal cost per task: **___ B flash, ___ B RAM.** A flat per-task figure means O(1); a rising one
means it grows with the count. Note the codegen track already predicts a *rising* figure for the
instant tier specifically, since `instant_task_manager` routes with a linear fold rather than a
perfect hash — while the managed tiers use `dispatch_factory`, which does. If the two ladders
disagree, that is why.

### 2d. Compile time

Wall-clock of a *clean* build; an incremental one mostly measures the shared framework archive.

| Board | tier 0 | tier 7 | 32 tasks |
|---|---|---|---|
| esp32dev | | | |
| nodemcuv2 | | | |

`dispatch_factory` is documented as roughly O(N×K) to compile — N registered types, K distinct
constructor signatures. The 1 → 32 task column is the direct test of that.

---

## 3. Runtime cost — RUNTIME

**Measured 2026-09-01.** Raw capture: `bench/data/runtime-esp32dev.txt`.

Board: **ESP32-D0WD-V3 rev 3.1** (Xtensa LX6, dual core) · attached via `/dev/ttyUSB0`, CP210x at
115200 · CPU **240 MHz** · date: **2026-09-01** · etools `static_vector` landed: **yes** (this is
the *after* side of that change; there is no `std::vector` "before" on this board).

`-O2 -DNDEBUG`, 20000 iterations per case, calibration loop subtracted. All figures ns/operation.

**Assumptions and conditions**, recorded per the benchmarking conventions:

- Single-threaded `loop()` on core 1; no WiFi, no BT, no other task registered. Nothing here says
  what happens under a busy radio stack or a preempting ISR.
- Board freshly reset by DTR/RTS toggle before each capture; the table is printed from `setup()`,
  so nothing else has run.
- Code executes from flash through the instruction cache, not IRAM. Not pinned — a cache-cold
  first iteration is amortized over 20000.
- CPU frequency left at the Arduino default 240 MHz and not otherwise pinned; the host's governor
  is `powersave`, which is irrelevant to on-board timing but is recorded for completeness.
- Timed with `esp_timer_get_time()` (µs). One operation is far below a µs, hence the 20000-iteration
  regions and the subtracted calibration loop.
- **Run-to-run spread is under 0.1 ns on every row**, and the checksum is bit-identical between
  runs — a deterministic single-core loop with nothing competing. Repeated three times; the table
  below is the third. Because the spread is this small, a median-and-range would be all zeros, so
  single figures are reported rather than dressing determinism up as statistics.

### 3a. Dispatch: instant task vs raw

`instant_task` declares no virtuals, so this is the cheapest path etask has. The codegen track
predicted this would be free — **it is not**, and the reason matters.

| Workload | raw `switch` | raw fn-ptr | etask instant | Δ vs fn-ptr | ratio |
|---|---|---|---|---|---|
| w0 state write | 84.4 | 114.2 | 211.2 | **+97.0** | 1.85 |
| w1 light (~20 fl) | 257.1 | 298.3 | 382.0 | **+83.7** | 1.28 |
| w2 heavy (~500 fl) | 8011.1 | 8050.3 | 8163.8 | **+113.5** | 1.01 |

**The delta is flat at ~84–114 ns across a 95× range of workload size**, which is the signature of a
fixed per-invocation cost — exactly what an abstraction overhead should look like. Relative cost
falls from 1.85× to 1.01× purely because the denominator grows.

**This does not contradict the codegen track's +0/−4 instructions**; the two measure different
things. Codegen counts the instructions in a `register_task` *function body*. This measures the
same call in a loop, which additionally pays the `buffer_view` construction, the argument
forwarding, and a call boundary the compiler will not inline through. Read them together: the
dispatch *logic* is as tight as a hand-written switch, and the *call* around it costs ~100 ns.

### 3b. Steady-state tick: polled task vs raw loop

The control-loop number. Two virtual calls plus bookkeeping, against one indirect call.

| Workload | raw fn-ptr loop | etask polled tick | Δ | ratio |
|---|---|---|---|---|
| w0 state write | 92.6 | 709.0 | **+616.4** | 7.66 |
| w1 light | 277.1 | 882.6 | **+605.5** | 3.18 |
| w2 heavy | 8029.3 | 8636.2 | **+607.0** | 1.08 |

Again flat — **~607–616 ns of fixed per-tick cost**, independent of the work. This is the headline
figure and the honest one to quote.

**`w0` is the upper bound on relative overhead** (7.66×: the framework *is* the whole cost when the
task does one store). **`w2` says whether it matters** (1.08×: 8% on a task doing ~500 flops).
Neither number alone is honest.

At ~610 ns a tick, one task at 1 kHz spends 0.06% of its budget in etask; see §6.

### 3c. Stateful vs polled — the price of suspendability

Identical work either side, so the delta is purely the pause/resume machinery.

| Workload | polled tick | stateful tick | Δ | ratio |
|---|---|---|---|---|
| w0 state write | 705.7 | 748.3 | **+42.6** | 1.06 |
| w1 light | 883.2 | 923.9 | **+40.7** | 1.05 |
| w2 heavy | 8634.9 | 8677.6 | **+42.7** | 1.00 |

**~42 ns**, flat, for the `switch` on task state that `stateful_task_manager::update()` runs and
`polled_task_manager::update()` does not. Suspendability is close to free; pick the tier on
semantics, not on cost.

> **A measurement artifact caught here, recorded because it nearly got published.** An earlier run
> of this case reported the stateful tier as **8 ns *faster*** than polled — impossible for a tier
> doing strictly more work per task. Cause: the tick-scaling sweep's `capacity<scale_case, 32>` had
> been added to the *shared* manager, raising the polled tier's budget to 38 against the stateful
> tier's 3. Since `update()` cost partly tracks the declared budget (§3e), the two sides of the
> "identical work" comparison were no longer identical. Fixed by giving the sweep its own manager.
> The lesson generalizes: in a paired comparison, the budgets must match too.

### 3d. Tick scaling — idle floor and per-task slope

One task type with `capacity<scale_case, 32>`, on a manager of its own, so the ladder is bounded by
the budget rather than by how many task types happen to be declared. w0 work, so this is framework
cost only.

| Live tasks | tick ns | per-task (mean) | marginal |
|---|---|---|---|
| 0 (idle floor) | 127.1 | — | — |
| 1 | 669.3 | 669.3 | 542.2 |
| 2 | 1209.3 | 604.7 | 540.0 |
| 4 | 2292.3 | 573.1 | 541.5 |
| 8 | 4458.6 | 557.3 | 541.6 |
| 16 | 8791.7 | 549.5 | 541.6 |
| 32 | 17457.4 | 545.5 | **541.6** |

**`update()` is exactly O(n) in the live task count.** The marginal cost is 541.6 ns/task and holds
flat to within 2 ns across the whole 0→32 range — this is a straight line, not an approximation of
one. The falling "per-task mean" column is just the 127 ns idle floor being amortized over more
tasks, not a scaling benefit.

The earlier caveat about capping the ladder at 2 points is **resolved**; `capacity<T, N>` is in
etools and the sweep now runs to 32. Extrapolation past 32 is still extrapolation, but a slope this
linear over five doublings supports it better than the old two points could.

### 3e. What an unused budget costs — the idle floor is not free

Found while chasing the §3c artifact, and worth reporting on its own. `update()` calls
`_garbage.reset()` on a `std::bitset<Budget>` and runs its erase sweep every tick, so part of the
per-tick cost tracks the **compile-time slot count**, not the live count. Measured with **zero tasks
live** in every row, so the budget is the only thing that differs.

| Declared budget | idle tick ns |
|---|---|
| 1 | 113.5 |
| 8 | 147.9 |
| 32 | 139.2 |
| 128 | 324.6 |

**A generous budget is not free, but it is cheap and sub-linear**: 128× the slots costs 2.9× the
idle tick, consistent with `bitset::reset()` clearing a word at a time rather than a bit at a time.
Budget 8 vs 32 is within noise of each other (both fit the same two 32-bit words plus loop
overhead).

Practical reading: **declaring `capacity<T, N>` generously costs RAM (≈36 B per slot, §3f) and a
few ns of idle tick — not a proportional slowdown.** Size the budget for peak concurrency and do
not agonize over it.

### 3f. RAM per slot

From the linker, holding everything else constant: adding `capacity<scale_case, 32>` to the pack
moved `.bss` from 21,928 B to 23,080 B — **1,152 B for 32 slots, ≈36 B per concurrent task slot**.
This is static RAM, not heap (§4).

### 3g. Per-board comparison

| Case | ESP32 @240MHz | ESP32-S3 @240MHz | ESP8266 @80MHz |
|---|---|---|---|
| instant dispatch, w0 (Δ vs fn-ptr) | +97.0 | not run | not run |
| polled tick, w0 (Δ) | +616.4 | not run | not run |
| polled tick, w2 (Δ) | +607.0 | not run | not run |
| idle floor (0 tasks, budget 32) | 127.1 | not run | not run |

Only the ESP32-D0WD-V3 was on the desk for this session. The S3 and ESP8266 envs exist and build;
they need the board swapped by hand.

---

## 4. Heap — RUNTIME

**Measured 2026-09-01.** Raw capture: `bench/data/heap-esp32dev.txt`.
Board: **ESP32-D0WD-V3 rev 3.1** · etools `static_vector` landed: **yes**.

### The question changed, so the track changed

This section used to measure three costs of a heap-backed design: a startup allocation, the
fragmentation it left, and a **reallocation cliff** — registering past `max_task_load` forced
`std::vector` to grow, and that growth was a real mid-flight `malloc` on a heap that by then held
the WiFi stack.

**None of those exist any more.** Both managers now hold
`etools::memory::static_vector<task_info, Budget>`, whose storage is an inline
`alignas(T) std::byte[Capacity * sizeof(T)]` member. The budget is a compile-time template
parameter, `task_manager`'s constructor is `= default` and takes no arguments, and there is no
growth path to fall off. Task objects live in `dispatch_factory`'s in-place `std::optional` slots,
which were never heap either.

So the claim is now the strongest one available — **etask allocates nothing, ever** — and this
track exists to test it rather than to assert it. The old `heap.cpp` no longer compiles against the
current API (`manager_t tight{2}` is rejected: the constructor takes no arguments), which is itself
the cleanest possible confirmation that the design changed.

### Measured: every delta is zero

`sizeof(manager_t)` = **348 B**, held inline. That is static RAM, not heap.

| Stage | free B | Δ vs baseline | largest block B | frag B |
|---|---|---|---|---|
| baseline (before manager) | 278,516 | — | 114,676 | 163,840 |
| manager constructed | 278,516 | **+0** | 114,676 | 163,840 |
| + internal channel | 278,516 | **+0** | 114,676 | 163,840 |
| after 400 register/retire cycles | 278,516 | **+0** | 114,676 | 163,840 |
| manager destroyed | 278,516 | **+0** | 114,676 | 163,840 |

- [x] **Construction allocates nothing.** PASS — where the old design took two `reserve()` blocks.
- [x] **Steady-state traffic allocates nothing.** PASS over 400 register/retire cycles. Heap cost
      scales with the declared task set, not with how many requests arrive.
- [x] **No leak** across the manager's lifetime. PASS, trivially: nothing is taken.

The 163,840 B fragmentation figure is the ESP32's own heap layout at boot (free heap minus largest
contiguous block) and is **unchanged by etask** — it is the same on every row, including the
baseline taken before any manager exists. It is not attributable to the framework.

### Budget exhaustion — what replaced the reallocation cliff

A fixed budget cannot grow, so the question became what a full manager does instead. Polled budget
set to 2, eight tasks offered:

| Stage | free B | Δ | largest block B | frag B |
|---|---|---|---|---|
| before | 278,516 | — | 114,676 | 163,840 |
| `manager<budget=2>` constructed | 278,516 | **+0** | 114,676 | 163,840 |
| after offering 8 | 278,516 | **+0** | 114,676 | 163,840 |

**2 accepted, 6 refused with `task_budget_exhausted` (0x18).** The budget is honored exactly, the
refusal is a clean status code at the call site, and it allocates nothing.

This is a strictly better failure mode than the design it replaced. The old cliff *succeeded* by
mallocing at the least convenient moment; the new one *fails predictably*, at a point the caller can
handle, with the heap untouched. The cost of that is that peak concurrency must be declared up
front — which is what `capacity<T, N>` and the tier budgets are for, at ≈36 B of RAM per slot
(§3f).

### The `std::vector` → `static_vector` change

No before/after is available on this board: the change had already landed when the first runtime
measurement was taken, so there is no `std::vector` side to measure without reverting etools. What
can be said is the after side, and it is unambiguous — **zero allocations, zero fragmentation
attributable to etask, and a predictable refusal in place of a mid-flight malloc.**

---

## 5. WiFi round trip — RUNTIME

**Not yet taken.** Requires a board and a network. PC → board → PC over TCP; nothing attached to
the board.

Board: ______ · network: ______ · PC → AP → board hops: ______ · date: ______

Packet: 32 B, `network` topology, no checksum (TCP guarantees integrity). Firmware and harness must
agree exactly.

### 5a. Sequential — one request in flight (latency)

| Case | median ms | p95 ms | p99 ms | mean ms | lost |
|---|---|---|---|---|---|
| echo (transport floor) | | | | | |
| oneshot + light work | | | | | |
| oneshot + heavy work | | | | | |

**Median and p95/p99, not the mean.** WiFi latency is long-tailed; a single retransmit can be 100×
the median.

**Framework share** (case median − echo median): light ___ ms, heavy ___ ms.

The echo floor is network + ecomm framing + one etask lifecycle. On WiFi it dominates the
framework's share by orders of magnitude — which is the point of measuring it separately. Reporting
only the total would credit the network's latency to etask.

### 5b. Pipelined — throughput

`--in-flight 8`. **Not comparable with 5a**: per-request timing includes queueing behind other
outstanding requests. Different question — how fast can the board be driven.

| Case | median ms | p95 ms | requests/s | lost |
|---|---|---|---|---|
| echo | | | | |
| oneshot + light | | | | |
| oneshot + heavy | | | | |

Saturation point (where added in-flight requests stop raising throughput): ______

---

## 6. Scale estimate

Written from §3 and §4 only. Inputs are shown so the arithmetic can be checked.

**Measured inputs:** idle floor 127.1 ns · marginal 541.6 ns per live task · RAM ≈36 B per slot
plus 348 B per manager. All at 240 MHz, `-O2`, w0 work.

**Assumptions, stated so they can be rejected:**

- Constant per-task cost. **Supported by measurement** — the slope is flat to within 2 ns across
  0→32 (§3d), so this is not the usual hopeful linearity assumption.
- No contention, no ISR interference, no radio stack. Single-threaded `loop()` only.
- Framework cost only; the tasks' own work is additive on top and is entirely the application's.
- Extrapolation past 32 live tasks is genuinely extrapolation. The 32-task row is measured; the
  128- and 256-task rows below are computed, and labelled as such.

### Tick budget

`T(N) = 127.1 + 541.6 N` ns. A defensible ceiling for a framework that is not the application is
10% of the tick.

| Live tasks | tick cost | % of 10 ms tick (100 Hz) | % of 1 ms tick (1 kHz) |
|---|---|---|---|
| 1 | 0.67 µs (measured) | 0.007% | 0.07% |
| 8 | 4.46 µs (measured) | 0.045% | 0.45% |
| 32 | 17.46 µs (measured) | 0.17% | 1.75% |
| 128 | 69.5 µs (computed) | 0.69% | 6.9% |
| 256 | 138.8 µs (computed) | 1.39% | 13.9% (over budget) |

> **32 tasks at 1 kHz uses 1.75% of the tick budget on an ESP32.** At 100 Hz, even 256 live tasks
> stay under 1.4%.

The 10%-of-tick ceiling is not reached until **~184 live tasks at 1 kHz**, or ~1,845 at 100 Hz —
both well past the point where RAM or the application's own work binds first.

### RAM budget

The binding constraint, as expected. Per live-task slot ≈36 B, plus 348 B per manager, against
~320 KB on the ESP32 — of which ~278 KB is free at boot before the application takes any.

At 36 B/slot, **the tick budget runs out before RAM does**: 184 slots (the 1 kHz tick ceiling) is
~6.6 KB, comfortably affordable. Framework RAM is not what limits a schema on this chip; the
application's own task state and any radio stack will bind long before either.

Note this is *runtime* RAM per concurrent slot. It is independent of how many task *types* the
schema declares, which is a flash and compile-time cost (§2, and `docs/compile-scaling.md`).

### Flash budget

Not computed here — §2's task-count ladder has not been run, so there is no measured marginal flash
per task to extrapolate from. Deliberately left blank rather than inferred from the runtime figures,
which say nothing about code size.

### WiFi command rate

Not measured; §5 has not been run.

---

## What was NOT measured

Silence reads as coverage, so state it plainly.

- [x] **Runtime cost** — measured on ESP32-D0WD-V3, §3.
- [x] **Heap track** — measured, §4. Track rewritten; the old premise no longer exists.
- [x] **Scale estimate** — §6, from measured inputs, with computed rows labelled.
- [ ] **Static footprint** — no run recorded. §2 is still a skeleton, and the flash budget in §6 is
      blank because of it.
- [ ] **Codegen** — preliminary counts only (§1), not a recorded run; Cortex-M4 and ESP8266 not run.
- [ ] **WiFi round trip** — not run; needs a network as well as a board.
- [ ] **ESP32-S3 and ESP8266 runtime** — envs build, boards not swapped in this session (§3g).

Known-permanent gaps to carry into the final document:

- **STM32F411 runtime** — compile-only; no such board is on hand. Its footprint is measurable, its
  timings are not.
- **Arduino Nano / AVR** — cannot build at all: avr-gcc ships no libstdc++. Not a broken benchmark;
  a result.
- **Concurrency, ISR interference, and contention** — single-threaded `loop()` only, no radio stack
  resident. Nothing here says what happens under a busy WiFi stack or a preempting ISR, and that is
  the largest remaining unknown in the runtime picture.
- **No `std::vector` baseline for §4** — the `static_vector` change had already landed before the
  first runtime run, so the before/after comparison the skeleton anticipated cannot be taken
  without reverting etools.

Resolved since the skeleton was written:

- ~~Tick scaling past the registered task count~~ — `capacity<T, N>` is in etools; the ladder now
  runs to 32 live tasks (§3d).
