# etask — working notes for Claude

## Resource limits: do not kill the machine

This is a 8-core / 15 GB workstation that the user is *actively working on*,
with an editor and browser already resident. Real headroom is around 6 GB, and
swap is usually partly in use before a build even starts.

Every etask translation unit instantiates deeply-nested variadic templates
(`dispatch_factory` over the whole task pack, `optimal_mph`, `typelist`), so
memory scales with the **task count of the schema**, not with the jobs flag.

**This has killed the user's editor three times.** Each time cost far more than
the build was worth. Twice it was `-j$(nproc)`; the third time it was
`pio run -j 1` on a 400-task project — *`-j 1` is not a safety net.*

### The hard rule

**Never run `pio run` on a schema over ~600 tasks on this machine. It cannot be
made safe by lowering the jobs flag.** Above that, measure on the host
(`cmake` + `size`) or don't measure at all. Report the ceiling to the user and
let them decide; do not go looking for a flag that makes it fit.

The ceiling was ~300 when a 400-task build needed 1.5 GB in one process. Two
etools fixes (`f05bc64` depth-flat tuple, `ea62c95` the destructor's `all_of`)
cut that; measured with the flags PlatformIO actually uses, `-Os -ggdb`:

| tasks | peak RSS, one process | time |
|------:|----------------------:|-----:|
| 260 | 660 MB | 6.6 s |
| 400 | 1,024 MB | 15.1 s |

Note these are **with debug info**, which is the configuration that ships:
`-ggdb` costs about +200 MB and +1.7 s at 260 tasks over plain `-Os`. Peak RSS
per process, not wall time, is what decides whether a build is safe — 1 GB at
`-j 8` is 8 GB, and there is ~6 GB.

### Below that ceiling

1. **`pio run` is strictly sequential and strictly one at a time.** Always
   `pio run -j 1`. Never two builds in one shell loop, never `&`, never
   overlapping a `pio` build with a `cmake` build.
2. **`cmake --build` gets `-j 2`**, and `-j 1` past ~100 tasks.
3. **Check headroom first, every time.** Under 4 GB available, do not start:
   ```bash
   free -m | awk '/^Mem:/ {print "available MB:", $7}'
   ```
4. **Build ladders one point at a time**, recording as you go, so an
   interruption costs one point rather than all five.

### Things that are not protection

- **`-j 1` is not protection.** See above: it OOM'd at 400 tasks.
- **`timeout` is not protection.** A long timeout just gives the OOM killer
  more time to find the build.
- **A "quick diagnostic" is not exempt.** `pio run --verbose`, `pio run` to
  inspect a flag, a "probe" build — these are full builds and killed the editor
  once already. If a question needs a large build to answer, the answer is
  "not measured", not "let me just try it".

### If it happens anyway

Exit code **137 is the OOM killer**, not a fault in the code being built. Stop,
tell the user, and do not retry the same command at a lower `-j`. The correct
response is to move the measurement to the host or drop it.

`scripts/measure_rtti.py` defaults to `--jobs 2` and is host-only, which is why
it is safe; `pio` is the dangerous path.

## Commit conventions

- Three `-m` flags: heading / description / API schematic.
- State what changed and what is still lacking. **Never first person**, and
  never the agent's reasoning.
- No `Co-Authored-By` trailer.
- Implementation and tests commit **separately**.
- Feature branch, merged to `main` once tests pass.

## Layout notes

- `project/**` is git-excluded by design (`.git/info/exclude`).
- Generated vs. user-owned: `generated/` is rewritten in full every run;
  `sys/`, `app`, `config/`, `hal/`, `support/` are scaffolded once and then
  owned by the user. Never clobber task bodies or prose.
- `integration/*/build` and `.pio` are ignored (`integration/.gitignore`).
