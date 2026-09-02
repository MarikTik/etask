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
| Largest schema that compiles in under 10 min | ~1,750 tasks |
| Largest schema before an hour per build | ~3,390 tasks |
| What binds first | **compile time**, not flash and not memory |

The binding constraint is not the device. A schema large enough to trouble a
1.3 MB flash budget is roughly three times larger than one that already takes
ten minutes to compile.

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

**This has since been fixed** (`50d3a46`). The heuristic was working correctly -
LLUT at two-byte uids really would have cost 131 KB - but the sparsity was
manufactured: uids were seeded from `blake2b(dotted_path)`, which scattered them
across the whole width for no benefit once the ledger existed to keep them
stable. Uids are now packed from zero, so `max_key` tracks the task count and
LLUT is selected again. Measured on the emitted table:

| tasks | hashed (FKS) | packed (LLUT) | saved |
|---:|---:|---:|---:|
| 260 | 10,696 B | 520 B | **10,176 B** |
| 400 | 11,584 B | 800 B | **10,784 B** |
| 600 | 22,000 B | 1,200 B | **20,800 B** |

More than the ~6.3 KB the cost model suggested, and it grows with task count
rather than being a fixed step. A lookup also drops from 29 instructions to 13,
and Clang - which spent 8.60 s constant-evaluating the FKS table - now compiles
the 260-task manager in 5.33 s rather than 13.68 s, since an LLUT array is
trivial to evaluate.

`uid:` was removed from the schema in the same change. A single high pin sets
`max_key` for the whole tree, so one of them defeated packing everywhere; it was
also a hole in the guarantee the ledger exists to provide, since a schema edit
could silently repoint a number a flashed device still associates with another
task. Retired uids stay reserved, so holes accumulate - but only `max_key`
matters for density, not contiguity.

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

Three changes, all in etools, all compile-time only:

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

### Rejected on measurement

Both of these are plausible enough to be proposed again, so they are recorded
with the numbers that killed them.

**A function-pointer table in place of `index_dispatch`'s fold.** The fold
expands N comparison arms at every call site, so collecting them into a table
looked like it would turn O(sites x N) code into O(N) data. Measured at 260
tasks: **45.30 s -> 48.57 s**, slightly *worse*. The dispatch fold was never the
bottleneck - it turned out to be the destructor, three sections up.

**Type erasure of the slot storage.** One `std::byte` cell sized to the widest
registered type, plus a `constexpr` table of `make`/`kill` function pointers,
replacing `array<optional<T>, N>` per type. The premise is sound - `optional<T>`
is where per-type-ness enters, since it must know `T`'s size, alignment,
constructor and destructor - and storage alone is dramatically cheaper:

| elements | typed storage | erased, storage only |
|---:|---|---|
| 260 | 1.60 s, 294 MB | 0.12 s, 52 MB |
| 520 | 3.49 s, 509 MB | 0.17 s, 63 MB |

But that store cannot construct or destroy anything. Adding the operations that
make it usable puts the per-type instantiations straight back:

| elements | typed | erased + vtable | time | memory |
|---:|---|---|---:|---:|
| 260 | 1.60 s, 294 MB | 1.86 s, 134 MB | **0.86x** | 2.20x |
| 520 | 3.49 s, 509 MB | 6.38 s, 259 MB | **0.55x** | 1.96x |

Compile time gets worse, and worse faster with N. Erasure does not remove
per-type work, it relocates it: two lambdas per type are still instantiated, and
constant-evaluating a 520-entry table of function pointers costs more than the
`optional` instantiations it replaced. The compile-time *memory* halves, but
memory is not the binding constraint - time is - so this would lower the
practical ceiling rather than raise it.

The runtime case is worse still. Two function pointers per task is ~2 KB of
flash at 260 tasks, and every cell must be sized to the *widest* task. Measured
`.bss` on the uniform synthetic schema, where waste should be near zero:

| elements | typed | erased |
|---:|---:|---:|
| 260 | 10,988 B | 12,752 B |
| 520 | 21,972 B | 25,488 B |

Already 16% worse where every task is the same size. Real schemas are
mixed-tier - `deep_tree` has instant, oneshot, polled and stateful tasks in one
tree - and a `stateful_task` with several members is far larger than an
`instant_task` with none, so cells sized to the largest could double or triple
RAM on a part with 320 KB. It would also trade `std::optional`'s exception
safety and `has_value()` invariant for a hand-maintained `live[]` array.

**Shorter generated type names.** With callgraph construction - the phase that
mangles every function's assembler name - at 76% of an 800-task build, and the
longest symbol name reaching 38,472 bytes, shortening the names the generator
emits looked like it would attack the dominant term directly. It does shorten
them, and it does not help:

| 800 tasks | `sub_000` / `task_0000` | `s0` / `t0` |
|---|---:|---:|
| total symbol-name bytes | 331,558 | 276,569 (-17%) |
| object | 825,896 B | 666,376 B (-19%) |
| **compile time** | **77.2 s** | **80.4 s** |

Names shrank and the build got slower. Two reasons. Itanium mangling already
substitutes repeated components, so the only part of a per-task fragment that is
not a back-reference is the task's own name - 39 bytes of fragment, of which a
name change moves six. And real schemas are already terse: `deep_tree`'s leaf
names average 4.8 characters, shorter than the synthetic `task_0000` this was
measured against, so a real project would see even less. The cost tracks the
*number* of distinct instantiations, not the length of what they are called.

**Splitting the manager across translation units.** With one TU costing 80 s,
giving each part of the manager its own file looked like it would at least
parallelise. Measured at 800 tasks, constructing the manager in one TU and
calling `register_task` from another:

| scenario | total CPU | wall at `-j 2` | peak RSS |
|---|---:|---:|---:|
| single TU | 80.4 s | 80.4 s | 1,734 MB |
| split, serial | 118.8 s | 118.8 s | 1,599 MB |
| split, parallel | 118.8 s | 77.0 s | **3,097 MB** |

Splitting adds 48% to total work, because each TU re-instantiates the whole
factory for whatever it touches - the manager's type is the pack, so naming it
anywhere pays for all of it. Running the halves in parallel recovers 3.4 s of
wall clock, 4%, in exchange for both compilers being resident at once: 3,097 MB
against 1,734 MB. On a machine whose whole problem is memory that is a bad
trade, and the guard in `CLAUDE.md` forbids it anyway.

Bisecting that TU is worth recording on its own, since it says where the cost
actually is: constructing the manager is 42 s, `register_task` adds 38 s, and
`update` and `complete_task` add nothing measurable. It is `dispatch()`
instantiating one body per registered type, which is intrinsic to the design.

The pattern across all four: replacing static dispatch with runtime tables cost
more than it saved, twice; shortening names attacked a symptom; splitting
duplicated the work. What did work - `meta::tuple` and the two closure removals
- deleted work that was pure overhead rather than trying to relocate work that
was not.

### The third fix: the destructor's emptiness check

The largest single win, and the one that took longest to find because it is not
where the cost appears to be.

`~dispatch_factory` asserted that every slot was unoccupied using `std::all_of`
with a lambda. libstdc++ does not pass a predicate to `all_of` directly: it
routes it through four adaptor class templates - `__ops::__pred_iter`,
`_Iter_pred`, `__negate`, `_Iter_negate` - each *parameterised on the predicate
type*. A lambda's closure type is a local class, so its mangled name embeds its
entire enclosing scope, which here is `dispatch_factory<...>::~dispatch_factory()`
with all 260 registered types spelled out: roughly 11 KB per name. Substitution
compression cannot help, because each of the 260 instantiations names a
different `optional<T>` iterator.

So four adaptors each re-encode an 11 KB name, 260 times over. The compiler
spends its time mangling and hashing strings rather than compiling code, and
`-ftime-report` names the pass: **callgraph construction, 12.34 s of 23.49 s
(53%)**, against 0.32 s for an equivalent hand-written loop. Template
instantiation was only 22%. In the object file, symbol names outweighed code by
an order of magnitude - 3,911 symbols over 5 KB long, 43 MB of mangled names,
against 271 symbols and 3 MB for the fixed version.

A range-for needs no adaptors, so nothing re-encodes the factory type. Same
semantics, same emitted code, and it beats the other candidate fix - hoisting
the predicate into a short-named helper, which shortens what gets amplified
rather than removing the amplifier (4.90 s vs 5.63 s at 260 tasks).

This is the same defect class as the `__PRETTY_FUNCTION__` problem above:
template-id text duplicated per instantiation. Both were invisible in profiles
that look at template instantiation, because neither is an instantiation cost.

### Current scaling

Manager-instantiating TU, after all three changes:

| tasks | before | after | speedup | peak RSS before | after |
|------:|-------:|------:|--------:|----------------:|------:|
| 260 | 18.0 s | **4.9 s** | 3.7x | 583 MB | 455 MB |
| 400 | 57.2 s | **11.7 s** | 4.9x | 981 MB | 709 MB |
| 600 | 202.3 s | **30.3 s** | 6.7x | 1,663 MB | 1,148 MB |
| 800 | 508.3 s | **73.2 s** | 6.9x | 2,386 MB | 1,644 MB |

("before" is after the `meta::tuple` change but before the destructor fix.
Against the original recursive-tuple code, 400 tasks was 153.7 s and 800 did not
finish in a reasonable time.)

Memory is now **1.87 MB/task**, near enough linear. Time scales as about
**N^2.71**, down from N^3.16; fitting the asymptotic regime gives
`time ~ 9.8e-7 * N^2.71` seconds:

| threshold | reached at |
|---|---:|
| 10 minutes | **~1,750 tasks** |
| 30 minutes | ~2,630 tasks |
| 1 hour | ~3,390 tasks |
| 4 GB RSS | ~2,140 tasks |

The ten-minute ceiling roughly doubled, from ~840 tasks to ~1,750.

**Time crosses into the intolerable well before memory does.** Whatever the
residual N^3 term is, it now sets the ceiling.

### Where the remaining cost is

Bisected again after the `meta::tuple` change, at 260 tasks. Each row is a
translation unit containing only what it names:

| what is compiled | time | RSS |
|---|---:|---:|
| `generated/task_list.hpp` - 260 adapters named | 0.17 s | 68 MB |
| the same, all types forced complete | 0.18 s | 68 MB |
| `dispatch_factory` **type** (pointer, never instantiated) | 0.27 s | 87 MB |
| `meta::tuple<array<optional<adapter>,1>...>` instance | 1.23 s | 303 MB |
| `dispatch_factory` **instance** | 3.94 s | 459 MB |
| `polled_task_manager` instance | **18.54 s** | 580 MB |
| full three-tier `task_manager` instance | 18.05 s | 582 MB |

Two conclusions. Naming types is free - 260 adapters cost 0.17 s, and completing
them adds nothing - so nothing about the *schema size* is inherently expensive.
And the factory is no longer the problem: it accounts for 3.94 s of the 18.05 s.

**About 14.6 s, or 78% of what remains, is `polled_task_manager` wrapping the
factory** - not etools. That is the next place to look, and it was invisible
while `std::tuple` dominated everything. `-DNDEBUG` changes nothing (18.16 s vs
18.29 s), so it is not the contract checks.

The `std::optional<Adapter_i>` instantiations that were the prime suspect turn
out to be 1.23 s of 18 - real, but not the ceiling. Type erasure would have
traded that 1.23 s for a larger cost elsewhere; see above.

### Non-issues, checked

- **`std::tuple` in eser.** Its tuples are per-task parameter lists, bounded by
  how many parameters a task declares (typically under ten), not by schema size.
  The recursive layout is fine at that scale and there is nothing to fix.
- **`meta::tuple`'s access strategy.** Resolving `get<I>` by overload against the
  unique `leaf<I, T>` base was compared against an explicit `static_cast` to the
  known base, which avoids forming an overload set: 1.35 s vs 1.33 s at 520
  elements. No difference; the current construction is already at the floor.
- **Every other `<algorithm>` call in the four libraries.** All four repositories
  were swept for the destructor's defect pattern - a lambda passed to a standard
  algorithm inside a template whose pack scales with the schema. Eleven candidate
  sites; the four that match structurally (`count_if`/`find_if` in
  `polled_task_manager` and `stateful_task_manager`) were measured and replacing
  all of them with hand-written loops changed a 260-task build by under 0.2 s,
  inside run-to-run noise.

  Two properties spare them, either sufficient on its own. Their lambdas capture
  `uid` **by value, not `this`**, so the closure type does not carry the factory
  type in its signature; and the iterated range is
  `static_vector<task_info, Budget>`, whose `iterator` is a plain `task_info*`
  (`static_vector.hpp:128`), so the adaptor templates are parameterised on
  `<task_info*, lambda>` - one mention of the pack, not 260. The destructor's
  range was a `meta::tuple` over every registered type, which is what let each
  adaptor layer re-encode the whole list.

  The lesson is therefore *not* "avoid `<algorithm>` inside variadic templates".
  It is that the danger needs a closure carrying the pack **and** a pack-shaped
  range. Worth re-checking if `task_info` ever becomes parameterised on the task
  types, or if the container becomes heterogeneous.
- **`is_distinct`'s recursion.** Clang's `-ftime-trace` appears to attribute 55 s
  to it, but that is *inclusive* time over 256 nested instantiations. Exclusive
  self-time is 0.61 s, and a standalone 260-type reproduction costs 0.14 s
  (0.19 s with realistic long names through the `bare_t` alias). Not a problem -
  and a caution that trace totals must be read as self-time.

### Debug info

The ESP32 Arduino build compiles with `-Os -ggdb`, so real firmware builds carry
full DWARF. Since the defect above was a *mangled-name* problem and DWARF
re-encodes the same names independently of the symbol table, it was worth
checking whether debug info re-amplifies it.

Manager TU at 260 tasks, GCC:

| flags | time | peak RSS | object | `.debug_*` |
|---|---:|---:|---:|---:|
| `-Os` | 4.89 s | 466 MB | 74 KB | 0 |
| `-Os -g1` | 5.14 s | 510 MB | 8.1 MB | 7.6 MB |
| `-Os -ggdb` | 6.63 s | 660 MB | 15.6 MB | 13.2 MB |

It does amplify, but sub-linearly: `-ggdb` cost +1.7 s on fixed code against
+6.9 s on the unfixed code. The amplification is mostly in *size* - before the
fix, DWARF turned a 1.4 MB object into 83 MB, with single `.debug_str` entries
up to 58 KB holding the full 260-type factory template-id.

**None of it reaches the device.** `firmware.elf` for `multi_link` is 5.9 MB, of
which 5.3 MB (90%) is `.debug_*`; the flashed `firmware.bin` is 256 KB. esptool
copies only loadable segments, and flash usage is byte-identical between `-ggdb`
and `-g0`. So debug info is build-time and disk cost only, and it buys working
backtrace decoding, which on ESP32 is what makes a panic address meaningful.

Recommendation: **leave `-ggdb` alone.** 1.7 s on a 260-task TU is a fair price
for decodable backtraces at zero firmware cost. `-g1` is worth documenting for
CI and bulk builds - it keeps line tables, so backtraces still decode, at half
the object size and within noise of no debug info at all. `-ggdb` and `-g` are
identical here in time, memory and DWARF bytes; there is no reason to prefer
one.

### Clang

Clang was installed late in this work, mainly for `-ftime-trace`. Two findings:

**etools did not compile under Clang at all** for a schema past 255 tasks.
`optimal_mph`'s FKS backend exceeds Clang's default constant-evaluation budget,
and the diagnostic points into `fks.hpp` rather than at anything the consumer
wrote. The limits had been raised in etools' `tests/CMakeLists.txt` but only for
the test targets; they are now on the `INTERFACE` target so consumers inherit
them (etools `ca8a993`).

**The FKS table costs Clang 62x what it costs GCC.** Same table, same 260 keys:

| | GCC 15 | Clang 21 |
|---|---:|---:|
| FKS table alone | 0.14 s | 8.74 s |
| full manager, 260 tasks | 4.91 s | 13.68 s |

`-ftime-trace` self-time attributes 8.60 s - 58% of Clang's entire compile - to
`EvaluateAsInitializer` on `fks_impl_singleton`. This is a weakness in Clang's
constant evaluator, not a defect in the table, which GCC builds in 0.14 s. **GCC
is the better compiler for this codebase**, by roughly 3x on a large schema.

## Practical ceilings

| constraint | ceiling | note |
|---|---:|---|
| ESP32 flash | ~4,800 tasks | extrapolated from <= 260 |
| Compile time, 10 min budget | ~1,750 tasks | measured to 800 |
| Compile time, 1 hour budget | ~3,390 tasks | projected |
| Host memory, 4 GB free | ~2,140 tasks | projected |
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
