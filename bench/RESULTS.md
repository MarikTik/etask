# etask benchmark results

**Status: pipeline laid out, measurements not yet taken.** This document is the skeleton — every
table, caveat and column is in place and deliberately empty. Fill a cell only from a run you can
point at, and cross-check it against the raw JSON in `bench/data/` before writing it here.

Two sections carry real numbers already, because they are headless and reproducible right now:
[§1 Codegen](#1-codegen-quality--compile-time) has preliminary instruction counts, marked as such.

---

## Provenance — what was measured

Record this for every run. A benchmark of a dirty tree is fine; one that does not say the tree was
dirty is not.

**Sibling commits at the time this skeleton was written (2026-08-27):**

| Repo | Commit | Dirty files |
|---|---|---|
| `etools` | `3d2797b` release: 1.1.1 | 4 |
| `ecomm` | `cd09249` release: 3.0.1 | 19 |
| `eser` | `bb683dc` release: 1.1.2 | 0 |
| `etask` | `cd026c9` build: trim the codegen extra to pyyaml | 3 |

etask branch: `milestone1/story1/task_tier_split#1`.

Regenerate before each run:

```bash
cd /home/mark/Desktop/projects/elib
for p in etools ecomm eser etask; do
  echo "$p $(git -C $p log --oneline -1) dirty=$(git -C $p status --porcelain | wc -l)"
done
```

### Two dirty trees that matter to the numbers

1. **`ecomm` (19 files).** Under active local development; its working tree differs from the
   published 3.0.1. Every `platformio.ini` in `bench/` sets
   `lib_extra_dirs = /home/mark/Desktop/projects/elib`, so **the working tree is what gets
   measured, not the registry versions `etask/library.json` declares.** Any number here that
   involves the external channel or the wire (static tier 7, the WiFi track) is a measurement of
   local ecomm.

2. **`etools` (4 files) — `static_vector` in progress.** At the time of writing,
   `etools/memory/static_vector.{hpp,tpp}` are new and untracked. This is the fix for the heap
   issue below, being done separately. **Any run taken before that lands measures the
   `std::vector` design**; label every runtime and heap figure with which side of that change it
   is on. The heap track exists precisely so there is a before/after.

### The ESP32 compile fix is in the measured tree

`etask/core/managers/detail/empty_managers.hpp` carries an uncommitted patch without which etask
does not compile for ESP32 at all. GCC 8.4 — shipped by the ESP32 Arduino core — cannot parse a
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

**Not yet taken. Requires a board; ask before flashing.**

Board: ______ · attached via: ______ · CPU MHz: ______ · date: ______ · etools `static_vector`
landed: yes / no

`-O2`, 20000 iterations per case, calibration loop subtracted. All figures ns/operation.

### 3a. Dispatch: instant task vs raw

`instant_task` declares no virtuals, so this is the cheapest path etask has. The brief anticipated
it might be unmeasurable, and the codegen track supports that.

| Workload | raw `switch` | raw fn-ptr | etask instant | Δ vs fn-ptr | ratio |
|---|---|---|---|---|---|
| w0 state write | | | | | |
| w1 light (~20 fl) | | | | | |
| w2 heavy (~500 fl) | | | | | |

If the instant delta is within noise, fall back to `oneshot` (below) as the reportable dispatch
figure, and say so rather than reporting a suspiciously round zero.

### 3b. Steady-state tick: polled task vs raw loop

The control-loop number. Two virtual calls plus bookkeeping, against one indirect call.

| Workload | raw fn-ptr loop | etask polled tick | Δ | ratio |
|---|---|---|---|---|
| w0 state write | | | | |
| w1 light | | | | |
| w2 heavy | | | | |

**`w0` is the honest upper bound on relative overhead** — the framework cost is the whole cost
there. **`w2` says whether it matters.** Report both; either alone misleads.

### 3c. Stateful vs polled — the price of suspendability

Identical work either side, so the delta is purely the pause/resume machinery the stateful manager
carries and branches on each tick.

| Workload | polled tick | stateful tick | Δ | ratio |
|---|---|---|---|---|
| w0 state write | | | | |
| w1 light | | | | |
| w2 heavy | | | | |

### 3d. Tick scaling — idle floor and per-task slope

The 0-task row is the idle floor: it runs every loop iteration of every project that links etask.

| Live tasks | tick ns | marginal per task |
|---|---|---|
| 0 (idle floor) | | — |
| 1 | | |
| 2 | | |

**Caveat, stated up front:** the current sweep is capped at the registered w0 task count, because
each task type reserves one concurrent slot by default. A wider ladder (4, 8, 16, 32 live) needs a
manager built with `capacity<T, N>`. Until that is done, **do not extrapolate the slope past what
was measured** — and if it is non-linear over the points that exist, say so and stop.

### 3e. Per-board comparison

| Case | ESP32 @240MHz | ESP32-S3 @240MHz | ESP8266 @80MHz |
|---|---|---|---|
| instant dispatch, w0 | | | |
| polled tick, w0 | | | |
| polled tick, w2 | | | |
| idle floor (0 tasks) | | | |

---

## 4. Heap — RUNTIME

**Not yet taken.** `pio run -e heap_esp32dev -t upload`.

Board: ______ · etools `static_vector` landed: yes / no

### What is actually on the heap

Being precise, because "the managers use unmanaged heap" reads worse than the truth. etask has
exactly **two** dynamic allocations:

- `polled_task_manager::_tasks` — `std::vector<task_info>`
- `stateful_task_manager::_tasks` — `std::vector<task_info>`

Both are `reserve()`d **once, in the constructor**, to `max_task_load` (default: the sum of every
task's declared concurrency). Registering and retiring tasks afterwards is `emplace_back`/`erase`
**within reserved capacity** — no per-task malloc. Task objects live in `dispatch_factory`'s
in-place `std::optional` slots, which are not heap at all.

So: **two allocations at construction, then a steady state.** Three costs remain, and each is
measured:

| Stage | free B | Δ vs baseline | largest block B | frag B |
|---|---|---|---|---|
| baseline (before manager) | | — | | |
| manager constructed (reserve) | | | | |
| + internal channel | | | | |
| after 400 register/retire cycles | | | | |
| manager destroyed | | | | |

- [ ] **Steady-state traffic allocates nothing.** 400 register/retire cycles must not move the
      heap. If it does, cost scales with traffic rather than with the declared task set — a much
      worse property, and the headline finding if it happens.
- [ ] **No leak** across the manager's lifetime.

### The reallocation cliff

A manager told to expect fewer concurrent tasks than it is given. The vector grows and *does*
malloc mid-flight, on a heap that by then holds the WiFi stack. The one heap behaviour that can
fail at runtime, so it is measured rather than argued away.

| Stage | free B | Δ | largest block B | frag B |
|---|---|---|---|---|
| before | | — | | |
| `manager{2}` constructed | | | | |
| after registering 8 (grew) | | | | |

Avoidable by declaring `max_task_load` ≥ peak concurrent tasks, which is the default.

### After `static_vector`

To be filled once the heap fix lands, as a direct before/after on the same board:

| Metric | `std::vector` | `static_vector` | Δ |
|---|---|---|---|
| heap at construction | | | |
| flash, tier 5 | | | |
| RAM (`.bss`), tier 5 | | | |
| polled tick ns, w0 | | | |

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

**Cannot be written until §3 and §4 have numbers.** Fill from measured inputs only, with the inputs
shown — an extrapolation whose inputs are visible is useful; a headline number is not.

State these assumptions explicitly, and abandon the extrapolation if the measured slope is
non-linear:

- constant per-task cost
- no contention
- no ISR interference
- extrapolation only within the measured range

### Tick budget

At 100 Hz one tick is 10 ms. With `update()` over N tasks costing T(N), a defensible ceiling for a
framework that is not the application is 10% of the tick.

> *N tasks at M Hz uses X% of the tick budget on an ESP32.*

| Task count | tick cost | % of 10 ms tick | % of 1 ms tick (1 kHz) |
|---|---|---|---|
| 1 | | | |
| 8 | | | |
| 32 | | | |

### Flash budget

Marginal flash per task against the 1.3 MB ESP32 default app partition: ______ tasks before
partitioning must change.

### RAM budget

eser's answer was 0 B; etask holds task state, so this will not be. Against ~320 KB on ESP32 this
is likely the binding constraint, not flash. Per-task RAM: ______ → ______ tasks.

### WiFi command rate

Bounds how often a PC-driven task can be commanded, independent of on-board cost: ______ Hz
sequential, ______ Hz pipelined.

---

## What was NOT measured

Silence reads as coverage, so state it plainly. As of this skeleton: **everything below is
outstanding.**

- [ ] Static footprint — no run recorded
- [ ] Codegen — preliminary counts only (§1), not a recorded run; Cortex-M4 and ESP8266 not run
- [ ] Runtime cost — no board attached yet
- [ ] Heap track — no board attached yet
- [ ] WiFi round trip — no board attached yet
- [ ] Scale estimate — blocked on the above

Known-permanent gaps to carry into the final document:

- **STM32F411 runtime** — compile-only; no such board is on hand. Its footprint is measurable, its
  timings are not.
- **Arduino Nano / AVR** — cannot build at all: avr-gcc ships no libstdc++. Not a broken benchmark;
  a result.
- **Tick scaling past the registered task count** — needs `capacity<T, N>`; see §3d.
- **Concurrency, ISR interference, and contention** — single-threaded `loop()` only. Nothing here
  says what happens under a busy WiFi stack or a preempting ISR.
