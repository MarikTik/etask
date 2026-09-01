# Compile-time and flash scaling

How an etask project's build cost grows with the number of tasks in its schema,
what drives each term, and where the practical ceilings are. Every number here
is measured on one machine (see [Test conditions](#test-conditions)); treat the
shapes as portable and the absolute values as not.

## Summary

| question | answer |
|---|---|
| Flash per task | ~218 bytes (~195 B `.text`, ~23 B `.rodata`) |
| One-off cost at 256 tasks | +6,315 bytes, an LLUT -> FKS switch |
| Largest schema that fits in ESP32 flash | ~4,800 tasks (extrapolated) |
| Largest schema that compiles in under 10 min | ~840 tasks |
| Largest schema that compiles at all here | ~1,500 tasks before an hour per build |
| What binds first | **compile time**, not flash and not memory |

The binding constraint is not the device. A schema large enough to trouble a
1.3 MB flash budget is roughly six times larger than one that already takes ten
minutes to compile.

## Flash

Measured on `esp32dev`, generated projects of uniform `polled_task`s, one
parameter and one return each, ten per scope.

| tasks | uid bytes | `.flash.text` | `.flash.rodata` | total |
|------:|----------:|--------------:|----------------:|------:|
| 10 | 1 | 123,939 | 53,748 | 194,055 |
| 50 | 1 | 130,611 | 54,756 | 201,735 |
| 100 | 1 | 140,171 | 55,908 | 212,447 |
| 200 | 1 | 160,303 | 58,212 | 234,883 |
| 255 | 1 | 171,071 | 59,476 | 246,915 |
| 260 | 2 | 172,195 | 65,908 | 254,471 |

Marginal cost per task:

| span | `.text` B/task | `.rodata` B/task |
|---|---:|---:|
| 10 -> 255 (1-byte uids) | 192.4 | 23.4 |
| 255 -> 260 (crossing) | 224.8 | 1,286.4 |

`.text` is flat throughout at ~195 B/task. The apparent explosion at the
boundary is entirely `.rodata`, and it is a step rather than a slope.

### The 256-task step

Task uids are `blake2b(dotted_path, digest_size=uid_bytes)`, so they are spread
uniformly across the whole uid space rather than allocated densely.
`dispatch_factory` keys on `etools::hashing::optimal_mph`, which picks a backend
from a compile-time memory model:

```
LLUT ~ K * sizeof(index_t)                              K = max_key + 1
FKS  ~ N * (3*index_t + 2*size_t + 1 + sizeof(KeyType))
use_fks = LLUT > FKS
```

At one-byte uids `K <= 256`, so LLUT costs 256 B and wins. At two-byte uids the
hashed keys reach toward 65,535, LLUT would cost 131,072 B, and the heuristic
flips to FKS. Confirmed in the symbol table:

```
255 tasks:   256 B  etools::hashing::details::llut_impl_singleton<unsigned char, ...>
260 tasks: 6,572 B  etools::hashing::details::fks_impl_singleton<unsigned short, ...>
```

A 6,316-byte increase, matching the 6,315 B measured above trend. Past the
boundary the per-task slope returns to normal - FKS grows about as slowly as
LLUT did.

This is the heuristic working correctly: LLUT at two-byte uids would cost 131 KB.
Allocating uids densely from the ledger's lowest free value would keep `max_key`
near N and let LLUT stay selected, recovering ~6.3 KB without changing the wire
format. Worth doing, but it is 0.5% of flash, not an emergency.

### Ceiling

At ~218 B/task against 1,310,720 B of flash, with ~250 KB of framework and
Arduino core baseline, the flash ceiling is roughly **4,800 tasks**. That is an
extrapolation from points at or below 260 and across a backend switch; treat it
as an order of magnitude.

## Compile time

The cost is concentrated in **one translation unit** - whichever one instantiates
the task manager (`app.cpp` in a scaffolded project). Everything else is cheap.

| translation unit | peak RSS | time |
|---|---:|---:|
| one task file (`sys/.../task_000.cpp`) | 61 MB | 0.4 s |
| `main.cpp` | 24 MB | 0.01 s |
| **`app.cpp`** (instantiates the manager) | **1,493 MB** | **153 s** |

Bisecting that TU at 260 tasks, before the `meta::tuple` change:

| what is compiled | time | RSS |
|---|---:|---:|
| naming `manager_t` only | 3.7 s | 788 MB |
| **constructing one instance** | **42.4 s** | 762 MB |
| raw `tuple<array<optional<adapter>,1>...>` | 3.5 s | 489 MB |
| `dispatch_factory` alone | 17.4 s | 715 MB |
| the FKS hash table alone | 0.14 s | 47 MB |
| `all_distinct_fast` alone | 0.06 s | 37 MB |

The cost was *constructing the factory* - not dispatch, not the hash table, not
the contract checks. `-fno-inline`, `-fno-exceptions` and `-O0` all changed
nothing (`-O0` was slower), so it was never the optimizer: the frontend emitted
198,790 lines of GIMPLE for a TU that yields seven functions, and the backend
had to process all of it before folding it away.

### What was fixed

Two changes, both in etools, both compile-time only:

1. **Contract messages** (`f9619f7`). The three `assert`s in `dispatch_factory`
   sat inside the class template, so `__PRETTY_FUNCTION__` expanded to the full
   template-id - naming every registered type. Cost was quadratic; at 100 tasks
   one string reached 1,183,522 bytes and `.flash.rodata` hit 1,262,324 bytes,
   overflowing flash by 162,677 bytes. Moving the checks to non-template
   functions taking plain integers dropped per-task rodata from 13,216 B to 24 B.

2. **Slot storage** (`f05bc64`). `std::tuple` is a recursive chain, so an
   N-element tuple is an N-deep hierarchy. `etools::meta::tuple` holds one
   `leaf<I, T>` per element as a direct base: depth O(1), `get<I>` a single
   deduction step.

   | elements | `std::tuple` | `meta::tuple` | speedup |
   |---:|---|---|---:|
   | 260 | 1.94 s, 383 MB | 0.60 s, 205 MB | 3.2x |
   | 520 | 9.72 s, 877 MB | 1.34 s, 374 MB | 7.3x |
   | 1040 | does not compile | 2.77 s, 714 MB | - |
   | 2080 | does not compile | 5.83 s, 1,395 MB | - |

   Past ~1000 elements `std::tuple` exceeds GCC's default `-ftemplate-depth` of
   900 and fails outright, which capped schema size for reasons unrelated to the
   target device.

An attempt to replace `index_dispatch`'s fold with a function-pointer table was
**rejected on measurement**: 45.30 s -> 48.57 s at 260 tasks. The dispatch fold
was never the bottleneck.

### Current scaling

Manager-instantiating TU, after both changes:

| tasks | time | peak RSS | MB/task |
|------:|-----:|---------:|--------:|
| 260 | 18.0 s | 583 MB | 2.24 |
| 400 | 57.2 s | 981 MB | 2.45 |
| 600 | 202.3 s | 1,663 MB | 2.77 |
| 800 | 508.3 s | 2,386 MB | 2.98 |

Against the same TU before the change: 260 tasks was 45.3 s / 835 MB and 400
tasks 153.7 s / 1,488 MB - so roughly **2.7x faster and 32% less memory**.

Memory grows as about **N^1.25**; time as about **N^3.16**. Fitting the
asymptotic regime gives `time ~ 3.4e-7 * N^3.16` seconds:

| tasks | projected time |
|------:|---------------:|
| 800 | 8.5 min (measured: 8.5 min) |
| 1,000 | 17 min |
| 1,200 | 30 min |
| 1,500 | 62 min |
| 2,000 | 153 min |

| threshold | reached at |
|---|---:|
| 10 minutes | ~840 tasks |
| 30 minutes | ~1,190 tasks |
| 1 hour | ~1,490 tasks |
| 4 GB RSS | ~1,530 tasks |
| 5.5 GB RSS | ~2,100 tasks |

**Time crosses into the intolerable well before memory does.** Whatever the
residual N^3 term is, it now sets the ceiling.

### Where the remaining cost is

The N distinct `std::optional<Adapter_i>` instantiations - one type per task,
each with its own constructor, destructor and `emplace`. No container change can
remove that; only type erasure would, at real runtime cost. Given 400 tasks now
compiles in under a minute, that is not obviously worth paying.

## Practical ceilings

| constraint | ceiling | note |
|---|---:|---|
| ESP32 flash | ~4,800 tasks | extrapolated from <= 260 |
| Compile time, 10 min budget | ~840 tasks | measured to 800 |
| Compile time, 1 hour budget | ~1,490 tasks | projected |
| Host memory, 4 GB free | ~1,530 tasks | projected |
| `std::tuple` depth (before `f05bc64`) | ~1,000 tasks | hard failure, now removed |

For a schema of a few hundred tasks none of these bind. `deep_tree`, the largest
integration project at 294 tasks, builds and verifies without trouble.

## Test conditions

- 8-core / 15 GB workstation, ~6 GB real headroom, editor and browser resident.
- Host: GCC 15, `-std=c++17 -Os`, one translation unit, `/usr/bin/time -v`.
- Target: `esp32dev`, PlatformIO with the Arduino core, GCC 8.4 (Xtensa),
  `xtensa-esp32-elf-size -A` for sections.
- Schemas generated by `mkschema.py`: uniform `polled_task`s, one `float`
  parameter, one `uint32` return, ten tasks per scope, one uart link.
- Real projects are mixed-tier and will differ in absolute terms. The scaling
  shapes should hold; the constants will not.
- Builds run one at a time, `pio run -j 1` / `cmake --build -j 2`, per the
  ceilings in `CLAUDE.md`. Large host probes are additionally run under
  `ulimit -v` so an over-run fails cleanly instead of invoking the OOM killer.
