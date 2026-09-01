# etask — working notes for Claude

## Resource limits: do not kill the machine

This is a 8-core / 15 GB workstation that the user is *actively working on*,
with an editor and browser already resident. Real headroom is around 6 GB, and
swap is usually partly in use before a build even starts.

Every etask translation unit instantiates deeply-nested variadic templates
(`dispatch_factory` over the whole task pack, `optimal_mph`, `typelist`). A
single compiler process routinely reaches **1–2 GB** on a large schema. Eight of
them do not fit. An OOM kill takes the user's editor down with it — this has
happened twice, and it costs far more than the build ever saves.

**Rules, in order of importance:**

1. **Never let a build default to `-j$(nproc)`.** `pio run` and `cmake --build`
   both do. Always pass an explicit jobs flag:
   - `pio run -j 2`
   - `cmake --build <dir> -j 2`
   - `make -j 2`
2. **One heavy build at a time.** Do not put builds of different projects in the
   same shell loop unless each is capped at `-j 1`/`-j 2` *and* they run
   sequentially. Never background a build with `&` to overlap it with another.
3. **Scale jobs down as the schema grows.** Past ~100 tasks use `-j 1`. A
   300-task project has 300 translation units, each pulling the full pack.
4. **Check headroom before a long build sequence**, and skip or serialize if it
   is thin:
   ```bash
   free -m | awk '/^Mem:/ {print "available MB:", $7}'
   ```
5. **Prefer measuring one build over rebuilding a ladder.** If a table needs
   five task counts, build them one at a time and record as you go, so an
   interruption costs one point rather than all five.
6. **`timeout` is not a memory guard.** A long timeout on a parallel build just
   means the OOM killer has longer to find it. Cap jobs instead.
7. If a command dies with **exit code 137**, that is the OOM killer, not a bug in
   the code being built. Reduce jobs and report it; do not simply retry.

`scripts/measure_rtti.py` already defaults to `--jobs 2` for this reason —
follow the same ceiling everywhere else.

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
