# bombardment

An integration test that overloads etask's task managers on purpose.

Its claim is narrow and worth stating precisely: **under sustained registration
at and past a tier's budget, the managers refuse work with the correct status
code and reclaim every record they hand out.** Not that they are fast, and not
that they are correct in general - that they degrade the way their documentation
says they do, rather than quietly.

## Running it

```bash
python3 verify.py            # configure, build, run, and judge the transcript
```

Exits 0 only if all eight checks ran and passed. `--no-build` reuses an existing
binary; `--build-dir` moves the build tree.

For the ESP32 target:

```bash
pio run -e esp32dev          # build
pio run -e esp32dev -t upload
pio device monitor -b 115200 # read the same transcript over serial
```

Both builds take etask from the checkout this project sits in, not from a
release. Testing a published etask would mean the result says nothing about the
headers next door - which are the ones being changed.

## What each check proves

| check | claim under test |
|---|---|
| `fill_to_budget` | a tier accepts exactly `budget` concurrent tasks, and they really occupy records |
| `budget_exhausted` | one past the budget is `task_budget_exhausted` (0x18) - for every uid, including ones with slots of their own free |
| `limit_reached_with_room` | saturating one uid while the tier has room is `task_limit_reached` (0x12), and the tier demonstrably still has room |
| `single_instance_refusal` | what a uid with the default `concurrency` of 1 answers when saturated - see the finding below |
| `slots_reclaimed` | records return when tasks conclude, so registration succeeds again. **The leak check** |
| `stateful_tier_is_separate` | the stateful tier has its own budget; exhausting the polled tier does not touch it, and an instant command still runs with both full |
| `paused_task_holds_its_record` | a paused stateful task still occupies its record |
| `sustained_churn` | 2000 rounds of register/complete leave the manager behaving exactly as the first check found it, with every constructed task also concluded |

The assertions are in `src/app.cpp`, because only C++ can call the manager -
there is no wire link here for a Python process to reach it through. `verify.py`
runs the harness and does the part it cannot do for itself: insist that every
expected check actually reported (a harness that stops early exits 0), check its
summary against its own transcript, and name the framework claim behind any
failure.

## Layout

| path | what it is | who owns it |
|---|---|---|
| `schema.yaml` | the task set, with budgets chosen so both refusals are reachable | you |
| `verify.py` | the host driver: build, run, judge | you |
| `CMakeLists.txt` / `platformio.ini` | the two builds | you |
| `src/host_main.cpp` | host entry point; runs the suite once and exits with the failure count | you |
| `src/main.cpp` | Arduino entry point, forwarding to `app::` | you |
| `src/app.{hpp,cpp}` | the checks themselves | you |
| `src/config/` | the composition root | you |
| `src/sys/**` | task bodies and scope contexts - created once, then yours | you |
| `src/generated/**` | task ids, per-tier task lists, scope accessors | the generator |
| `.schema.uids.json` | the uid ledger - commit it | the generator |

## Findings

Two places where the managers' behaviour and the status codes' documentation did
not line up. Neither is a crash, and both are the kind of thing only a test that
deliberately reaches the limit would ever see.

**Both were resolved in the documentation rather than the code** (2026-09-01).
The behaviour in each case is defensible and is now pinned by the checks here;
what was wrong was the wording that described it. The findings are kept below
because the *constraint* in finding 2 is still real, still unenforced, and still
easy to violate by accident.

### 1. A saturated single-slot uid reports `duplicate_task`, not `task_limit_reached`

**Status: docs corrected; behaviour unchanged and pinned by
`single_instance_refusal`.**

`task_limit_reached` (0x12) was documented as "this task type's own concurrency
cap is reached: every slot its `capacity<Task, N>` reserves is occupied". A uid
with no `concurrency:` in the schema reserves one slot, and one live instance
occupies it - so by that wording, the second registration should have been 0x12.
Both managers instead special-case a cap of one:

```cpp
if (running_count >= max_concurrent)
    return max_concurrent > 1 ? status_code::task_limit_reached
                              : status_code::duplicate_task;
```
*(`etask/core/managers/polled_task_manager.tpp:48`, and identically at
`stateful_task_manager.tpp:48`)*

`duplicate_task` (0x13) was documented as "duplicate instance disallowed by
policy" - a rule *against* running two, which is a different thing from the one
slot allowed being in use. A caller distinguishing "retry when a slot frees"
from "never, this task is exclusive" was told the wrong one, and since
`concurrency: 1` is the schema default, that is the case most real tasks are in.

`status_code.hpp` now says what actually happens: 0x12 and 0x13 are the same
condition split by cap size, 0x13 is the ordinary "already running" answer for a
default-concurrency task, and both are retry-when-free rather than permanent.

### 2. A uid whose `concurrency` equals its tier's `budget` can never report `task_budget_exhausted`

**Status: documented in `status_code.hpp`, both managers' `register_task`, and
the schema reference in the top-level README. Still unenforced.**

The per-uid cap is tested before the tier's:

```cpp
if (running_count >= max_concurrent) return ...;                     // 0x12 / 0x13
if (_tasks.full())  return status_code::task_budget_exhausted;       // 0x18
```

When both are spent at the same registration the per-uid answer wins. So a tier
whose budget is 6, holding six instances of a uid capped at 6, refuses the
seventh with `task_limit_reached` - and the caller raises that task's
`concurrency`, which changes nothing, because the tier was the binding
constraint all along.

The ordering itself is defensible: the narrower cause is the more specific
answer, and when both are true either is arguably correct. What made it worth
recording is that the two codes are documented as distinguishing conditions the
caller should react to differently, and at the exact point where they coincide
the more actionable one is the one suppressed.

This test sidesteps it by construction - every uid in `schema.yaml` is strictly
narrower than its tier's budget, and the tier is filled by combining two uids
rather than repeating one. **That constraint is now written down in all three
places a user might look, but nothing checks it**, and `concurrency: 4` on a
tier budgeted at 4 is a natural thing to write. Rejecting it at generation time
is the obvious next step and has not been done.

### Not a finding: no leaks

Under 2000 churn rounds the harness registered 8000 tasks and observed 8000
completions, with the tier still filling to exactly its budget and refusing at
exactly the right point afterwards. The `swap_erase` compaction in `update()`
permutes the record storage on every sweep, and nothing was mislaid across
thousands of them.
