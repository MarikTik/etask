# etask benchmarks

**Status: pipeline laid out, not yet run.** Everything here compiles and the two headless tracks
execute; no measurement has been recorded. `RESULTS.md` is a skeleton with the tables and caveats
in place and no numbers in them. Two things are deliberately pending:

1. **The heap issue** — `polled_task_manager` and `stateful_task_manager` each hold a
   `std::vector<task_info>`. Being resolved separately; the runtime and heap tracks are written to
   measure the current design so there is a before/after.
2. **Hardware runs** — one USB port, boards swapped by hand. Ask before flashing.

---

## The question this suite answers

**What does an etask task cost against the same work invoked directly?** Concretely: the framework
replaces a hand-written `if`/`switch` on a uid plus a function-pointer call with a virtual
dispatch through `dispatch_factory`. Every runtime case here is a **paired comparison** of exactly
that — identical work, reached two ways — so the delta is attributable to the framework and not to
differently-written work.

Four tracks. Only the last two need hardware.

| Track | Command | Hardware |
|---|---|---|
| Codegen quality (instruction counts) | `bench/scripts/codegen.sh [host\|xtensa\|xtensa32\|arm]` | no |
| Static footprint + compile time | `python3 bench/scripts/measure.py` | no |
| Runtime cost per task, and the heap track | `cd bench/runtime && pio run -e esp32dev -t upload` | **yes** |
| WiFi round trip (PC → board → PC) | `cd bench/wifi/firmware && pio run -e esp32dev -t upload` | **yes + WiFi** |

Run them in that order: the two headless tracks are fast, need nothing plugged in, and the codegen
one is the strongest single result.

---

## What is measured against what

The abstractions under scrutiny, per the brief: `etools::memory`,
`etools::factories::dispatch_factory`, and the virtual calls. Each is isolated somewhere:

| Abstraction | Where it is isolated |
|---|---|
| `dispatch_factory` perfect-hash routing | codegen comparison 4, against a hand-written `switch` that placement-news the same types |
| The instant tier's linear uid fold | codegen comparisons 1 and 2, at 4 and 16 tasks — the pair shows whether it grows |
| Virtual `on_execute` + `is_finished` per tick | codegen comparison 3, and the runtime `polled` rows |
| Pause/resume machinery | runtime: `stateful` vs `polled`, identical work either side |
| `std::vector<task_info>` on the heap | the heap track |
| ecomm packet + eser codec on the wire | static tier 6 → 7, and the WiFi echo case |

### Two "raw" references, not one

"Raw code" is not one thing, and picking only one biases the answer:

- **`raw_switch`** — a `switch` calling a *direct* function, which the compiler may inline
  entirely. The fastest hand-written dispatch there is. Comparing only against this **overstates**
  etask's cost, because it charges etask for indirection any extensible design would also pay.
- **`raw_fnptr`** — a `switch` selecting a function pointer from a `volatile` table, then calling
  through it. Not devirtualizable, which is the same constraint a virtual call works under.
  Comparing only against this **understates** etask's cost.

Both are in the runtime table. The `volatile` on the table is load-bearing: without it the compiler
folds the pointer back into a direct call and the comparison silently becomes "inlined work vs
virtual work".

### Three workload sizes

Abstraction overhead is a *fixed* per-invocation cost, so its significance is entirely relative to
the work it wraps. Every runtime case runs at three sizes:

| | Work | What it represents |
|---|---|---|
| `w0` | one `volatile` store | A state change — `stop`, a setpoint write. The framework cost *is* the whole cost: the honest upper bound on relative overhead. |
| `w1` | ~20 flops | A sensor conversion, one PID step. |
| `w2` | ~500 flops | A filter update, a small matrix step. |

Read the table by column: **`w0` says how expensive the abstraction is; `w2` says whether anyone
should care.** Publishing only one of them would be the misleading choice in either direction.

---

## 1. Codegen quality (no hardware)

```bash
bench/scripts/codegen.sh host       # x86-64
bench/scripts/codegen.sh xtensa32   # ESP32 core's GCC 8.4
bench/scripts/codegen.sh xtensa     # ESP8266 core's GCC 10.3
bench/scripts/codegen.sh arm        # Cortex-M4, compile-only
```

Compiles `bench/codegen/cg.cpp` and counts instructions per `extern "C"` symbol. `extern "C"` does
double duty: it stops name mangling so the disassembly can be sliced by symbol, and it stops the
functions being inlined into nothing, which would report every comparison as free.

The work in each case is a single `volatile` store — deliberately, since this track measures
*dispatch* and any real workload would swamp it.

**Two early observations** (host and ESP32 GCC 8.4, `-O2`) — recorded here because they are already
reproducible, and both are pending confirmation in `RESULTS.md`:

- Instant dispatch is **instruction-identical to a hand-written switch on x86-64** (+0 at both 4
  and 16 tasks), and on Xtensa it is **smaller** (−4 at 4 tasks, −46 at 16). The fold compiles to a
  tighter comparison chain than GCC's jump-table lowering of the equivalent `switch`.
- `dispatch_factory::emplace` costs roughly 2× a hand-written placement-new `switch` (+61 host,
  +48 Xtensa). Read this alongside the runtime numbers: it is one-time construction cost, not
  per-tick.

A negative delta is a real result, not an error — but it means the fold beat the compiler's switch
lowering on that target, **not** that etask is free. The runtime table is what settles cost.

## 2. Static footprint (no hardware)

```bash
python3 bench/scripts/gen_ini.py > bench/platformio.ini   # 168 envs
python3 bench/scripts/measure.py                          # everything
python3 bench/scripts/measure.py --boards esp32dev --modes rel
python3 bench/scripts/measure.py --ladder tier            # feature ladder only
python3 bench/scripts/measure.py --ladder tasks           # scaling ladder only
python3 bench/scripts/measure.py --json bench/data/static.json
```

`platformio.ini` is generated — edit `scripts/gen_ini.py` and regenerate rather than hand-editing,
or the environments drift apart and the ladder stops subtracting cleanly.

**Feature ladder** (`-D BENCH_TIER=n`), each step one feature:

| Tier | Adds |
|---|---|
| 0 | framework + sink only, etask not included — the floor |
| 1 | `#include <etask/core/core.hpp>`, nothing instantiated |
| 2 | `task_manager` with 1 instant command |
| 3 | + a 2nd instant command → marginal cost of one instant task |
| 4 | + the polled tier → vector, bitset, `dispatch_factory`, vtables |
| 5 | + the stateful tier → full framework |
| 6 | + internal channel |
| 7 | + external channel → pulls in the ecomm packet and eser codec |

**Tier 1 is the honesty check.** etask claims header-only, so including it while instantiating
nothing must cost **exactly 0 bytes**. `measure.py` checks this and prints PASS or the delta; eser
measured +0 on every board and mode, and etask is held to the same bar.

**Task-count ladder** (`-D BENCH_TASKS=n` at tier 5): 1, 2, 4, 8, 16, 32 registered tasks. The
slope is the marginal flash cost per task, and says whether dispatch is O(1) or O(n) in code size.
The eser suite had no equivalent; this is the number that answers "how good is it at full scale".

**Build modes:** `rel` (`-Os -DNDEBUG`, ships), `relO2` (`-O2 -DNDEBUG`), `dbg` (`-Og`, asserts
live). The debug column is not redundant — etask's contracts are `assert`, which exists only while
`NDEBUG` is undefined. In eser they cost 2.5–6× the shipping footprint.

### Two behaviours in `measure.py` that must not be removed

1. **`verify_flags()`** parses the real compile line from `pio run -v` and asserts the intended
   `-O` and `NDEBUG` actually arrived. Wrong numbers otherwise look entirely plausible. This
   caught two genuine errors while the eser suite was built.
2. **Architecture-matched `size` tool**, chosen from the ELF's `e_machine`. The host `size` on a
   cross ELF silently reports nothing, which reads as a real size change.

### Do not parallelise

Six concurrent Xtensa builds invoked the OOM killer on this machine (exit 137), and it also
destroys the compile-time column, which would then measure contention. Sequential is ~4 s per
environment. There is no `-j`, on purpose.

### The `build_unflags` trap

PlatformIO applies `build_unflags` **after** `build_flags`. Listing `-Os -O2 -Og` there strips the
optimization level you are setting, leaving the build at `-O0`. On ESP8266 this once reported
13600 B where the truth was 888 B. **Only unflag the language standard** — plus `-DNDEBUG` in debug
envs, where STM32duino injects it regardless.

## 3. Runtime cost (needs a board)

```bash
cd bench/runtime
pio run -e esp32dev -t upload         # the paired-comparison table
pio run -e heap_esp32dev -t upload    # the heap track
```

Envs: `esp32dev`, `esp32s3`, `nodemcuv2`, and a `heap_*` variant of each. `-D BENCH_HEAP` swaps
`src/main.cpp` out for `src/heap.cpp`; both are wrapped in the matching guard so exactly one
defines `setup()`/`loop()`.

Cases:

- **instant vs raw dispatch** — no vtable, no storage, no reply. The brief guessed this might be
  unmeasurable; `instant_task` genuinely declares no virtuals, so that guess is well-founded, and
  the codegen track already shows +0 on x86-64. `oneshot` is measured too, as the fallback.
- **polled `update()` tick vs a raw loop** — the per-tick cost of a live task: two virtual calls
  plus the manager's bookkeeping, against one indirect call. This is the number a control-loop
  budget is built from.
- **stateful vs polled** — identical work, so the delta is purely the pause/resume machinery.
- **tick scaling** — the idle floor (0 live tasks, which runs every loop iteration of every
  project) and the marginal per-task tick cost.

Timing: `esp_timer_get_time()` on ESP32, `micros()` on ESP8266. A single operation is far below one
clock tick, so each case runs 20000 iterations and divides, **subtracting a calibration loop of
identical shape**.

### Reading the serial output

`pio device monitor` needs a TTY and crashes in a non-interactive shell. Read the port with
pyserial, toggling DTR/RTS to reset so `setup()` output is captured:

```python
import serial, time
p = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
p.dtr = False; p.rts = False; time.sleep(0.1)
p.dtr = True;  p.rts = True                      # reset, so setup() re-runs
deadline = time.time() + 30
while time.time() < deadline:
    line = p.readline()
    if line: print(line.decode(errors='replace'), end='')
```

### Identify the chip before every flash

Do not infer it from the USB descriptor — an ESP32-S3 in a prior session enumerated as `10C4:EA60`
(CP2102), the same descriptor a classic ESP32 presents:

```bash
$(head -1 $(which pio) | sed 's/^#!//') \
  ~/.platformio/packages/tool-esptoolpy/esptool.py --port /dev/ttyUSB0 chip_id
```

### The heap track

etask has exactly **two** dynamic allocations: `polled_task_manager::_tasks` and
`stateful_task_manager::_tasks`, both `std::vector<task_info>`, both `reserve()`d **once in the
constructor**. Registering and retiring tasks afterwards is `emplace_back`/`erase` within that
reserved capacity — no per-task malloc. Task objects themselves live in `dispatch_factory`'s
in-place `std::optional` slots, which are not heap at all.

So "the managers use unmanaged heap" is true but narrower than it sounds, and the track measures
the three costs that actually remain:

1. **Startup allocation** — two blocks, sized by `max_task_load`.
2. **Fragmentation** — free heap minus largest free block. Those two blocks are allocated early and
   never freed (the benign case), but an over-declared `max_task_load` wastes RAM permanently.
3. **The reallocation cliff** — register more concurrent tasks than `max_task_load` and the vector
   *does* malloc mid-flight, on a heap that by then holds the WiFi stack. This is the one case that
   can fail at runtime, so it is measured explicitly rather than argued away.

The track also asserts that steady-state traffic (400 register/retire cycles) allocates **nothing**,
and prints PASS or the delta.

## 4. WiFi round trip (needs a board and a network)

```bash
cd bench/wifi/firmware
pio run -e esp32dev -t upload \
  --project-option='build_flags=-std=gnu++17 -O2 -DNDEBUG -DBENCH_PORT=3333 -DBENCH_SSID="net" -DBENCH_PASS="pw"'
# read the IP the board prints at 115200, then:
python3 ../roundtrip.py --host <that-ip>
python3 ../roundtrip.py --host <that-ip> --in-flight 8      # throughput
```

Credentials are build flags so they are never committed; they default to placeholders.

The PC harness and the firmware must agree on the packet shape **exactly** — 32 bytes, `network`
topology (so replies can be addressed back), no checksum (TCP already guarantees integrity, and a
CRC here would put ecomm's checksum into every measurement). A mismatch produces silent framing
errors, not a diagnostic.

Uids the firmware registers: `0x20` echo (no work), `0x21` light, `0x22` heavy, `0x10` instant
(**no reply** — the tier's contract, so it measures one-way throughput only).

**Median, p95 and p99 — not the mean.** WiFi latency is long-tailed; a single retransmit can be
100× the median, and a mean folds that into a figure nobody experiences. For a control loop the
tail is what decides whether a deadline is met.

**The echo case is subtracted from the others.** It is the transport floor — network plus ecomm
framing plus one etask lifecycle — and on WiFi it dominates the framework's own share by orders of
magnitude. Reporting only the total would credit the network's latency to etask, or hide etask
inside it. The confounder here is the network, not the code.

`--in-flight N` pipelines requests, which measures throughput rather than latency and exposes
whether the board's single-threaded `update()` loop saturates. Those numbers are deliberately
**not** comparable with the sequential ones: per-request timing there includes queueing.

Lost replies are counted and reported. WiFi drops packets; silently retrying would hide real loss
behind a flattering latency figure.

---

## Environment

The harness needs the local siblings, not the registry. `etask/library.json` declares registry
deps (`MarikTik/ecomm ^3.0.1`, `MarikTik/etools ^1.1.1`), but **`ecomm` is under active local
development and its working tree differs from the published version** — a registry build measures
different code. Every `platformio.ini` here therefore sets:

```ini
lib_extra_dirs = /home/mark/Desktop/projects/elib
lib_ldf_mode = deep+
```

`lib_extra_dirs` takes precedence over `library.json`, but `RESULTS.md` must say so, so nobody
assumes the published versions were measured. Record the commits:

```bash
cd /home/mark/Desktop/projects/elib
for p in etools ecomm eser etask; do
  echo "$p $(git -C $p log --oneline -1) dirty=$(git -C $p status --porcelain | wc -l)"
done
```

A benchmark of a dirty tree is fine. A benchmark that does not say the tree was dirty is not.

For the Python tracks, `ecomm-python` and `etask-python` must be importable, and `ecomm-python`
needs `beartype` (absent from the system interpreter — use its venv):

```bash
cd /home/mark/Desktop/projects/elib
PYTHONPATH=ecomm/ecomm-python/src:etask/etask-python \
  ecomm/ecomm-python/.venv/bin/python etask/bench/wifi/roundtrip.py --help
```

PlatformIO also needs `intelhex` in its own interpreter for ESP32 builds:

```bash
$(head -1 $(which pio) | sed 's/^#!//') -m pip install intelhex
```

Toolchains are already installed machine-wide (`~/.platformio/packages`, 4.8 GB) and are not
per-project. `<project>/.pio/` is not shared and regenerates in ~4 s per environment; it is
gitignored.

**Compiler versions matter here.** ESP32 and ESP32-S3 ship **GCC 8.4**; ESP8266 ships **GCC 10.3**.
Both are older than the host compiler, so C++17 that builds on the desktop can fail on target — see
`project/benchmarking-brief.md` §2b and the note in `etask/core/managers/detail/empty_managers.hpp`.
Compile for the target early.

---

## Reporting standards

Carried over from the brief, and binding:

- **Never publish a number you have not traced to its source.** Cross-check rendered tables against
  the raw JSON.
- **State what was not measured.** Silence reads as coverage.
- **Distinguish absolute totals from deltas.** A tier-7 total including a 233 KB framework floor is
  not "etask costs 233 KB".
- **Label every heading COMPILE-TIME or RUNTIME**, and say which board and how it was attached.
- **Ask before flashing** — it overwrites whatever is on the board.
- If a result flatters the framework implausibly, it is measuring an artifact. Chase it down before
  publishing it. In eser, both hygiene fixes *raised* the reported cost.
