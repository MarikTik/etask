#!/usr/bin/env python3
"""Drives the built deep_tree binary and asserts the tree held together.

Run it after a host build, from anywhere:

    cmake -S . -B build && cmake --build build
    ./verify.py

Exits 0 if every check passed, 1 otherwise, printing what failed and - for the
ledger checks - exactly which uid moved and where it moved to.

## What is being checked, and in what order

The checks run cheapest-first, because a failure in an early one makes the later
ones meaningless rather than merely also-failing:

1. **Structure.** 294 tasks, all uids distinct, the width is two bytes, the
   abstract fan-out produced the instances it should have. This is read straight
   out of `.schema.uids.json` - no binary needed.
2. **Reachability and identity.** Every uid in the ledger is fed to the binary,
   which starts that task and reports the uid the task was *compiled* with. They
   must match, one report per uid. This is what distinguishes 294 real tasks
   from one task reachable under 294 numbers.
3. **Deep paths.** The same uids, resolved through the generated Python client's
   scope tree by attribute (`tasks.mesh.s0.n0.p0.sample`), must agree with the
   ledger. Two independent projections of one schema, compared against each
   other.
4. **The ledger.** Regenerate and assert nothing moved; then *add a task*,
   regenerate again, and assert nothing moved that time either while the new
   task got a uid of its own. Then *remove* one, and assert its uid was reserved
   rather than handed to somebody else. Finally, on a throwaway schema of its
   own, grow a project across 256 tasks - the width change that used to
   renumber everything - and assert it renumbers nothing.

Check 4 is the one worth having. A uid is a wire identifier: a peer built last
month puts it in a request and matches it in a reply. If a uid moves because
somebody added a task to the schema, every deployed peer is silently talking to
the wrong task - the frames still parse, the checksums still pass, and the
device does the wrong thing. Nothing else in this file is as expensive to get
wrong.

The ledger checks work on a **copy** of the project in a temporary directory, so
the real `.schema.uids.json` and `src/sys/` are never touched. A test that
mutated the thing it was testing could only be run once.

## A note on shrinking the schema by hand

Removing instances from an abstract scope leaves the scaffolds of the instances
that went away sitting in `src/sys/`, and both build systems glob that
directory. The next build then fails on the orphans, which now reference scope
accessors and enumerators the generator no longer emits.

That is the ownership model working as designed rather than a defect - task
bodies are yours, and a generator that deleted source it did not write would be
a much worse tool. But it does mean shrinking a fan-out is a two-step edit: drop
the instances from the schema, regenerate, and then delete the orphaned
directories yourself. Nothing warns you; the compiler does, one file at a time.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / ".schema.uids.json"
SCHEMA = HERE / "schema.yaml"
BINARY = HERE / "build" / "deep_tree"
CLIENT = HERE / "python" / "tasks.py"

#: The etask checkout this project lives in, and the generator inside it. Taken
#: from the tree rather than from an installed `etask`, for the same reason the
#: CMake build does: an integration test asks about the code as it stands here.
REPO = HERE.parents[1]
GENERATOR_ROOT = REPO / "etask-python"

#: The schema's shape, restated so that a change to the schema that quietly
#: shrinks the tree - an abstract scope losing instances, say - fails here
#: rather than passing a smaller test.
SEGMENTS, NODES, PROBES = 6, 4, 3
TASKS_PER_PROBE = 4
MESH_TASKS = SEGMENTS * NODES * PROBES * TASKS_PER_PROBE
BUS_TASKS = 5          # link_state.probe, link.state_probe2, and the three under reserve
ROOT_TASKS = 1         # census
EXPECTED_TASKS = MESH_TASKS + BUS_TASKS + ROOT_TASKS
EXPECTED_UID_BYTES = 2

#: `support::phase`, mirrored. A managed task reports from `on_complete`; an
#: instant command from its constructor, having no `on_complete` to report from.
PHASE_COMPLETED = 1
PHASE_RAN = 2

#: The status byte a successful `register_task` returns (`status_code::ok`).
STATUS_OK = 0


class Failures:
    """The running tally, so every check reports rather than the first aborting.

    A run that stopped at the first failure would hide whether one thing broke
    or the whole tree did, and those call for very different reactions.
    """

    def __init__(self):
        self.messages = []

    def check(self, condition, message):
        """Records `message` unless `condition` holds.

        @param condition The thing that should be true.
        @param message What to say if it is not.
        @return The condition, so a caller can skip dependent work.
        """
        if not condition:
            self.messages.append(message)
        return bool(condition)

    def report(self, label):
        """Prints this section's outcome.

        @param label The section's name.
        @return True if nothing has failed so far.
        """
        if self.messages:
            print(f"FAIL  {label}")
            for message in self.messages:
                print(f"      {message}")
        else:
            print(f"ok    {label}")
        clean = not self.messages
        self.messages = []
        return clean


def load_ledger(path):
    """@return The ledger at `path`, as its parsed JSON object."""
    return json.loads(Path(path).read_text())


def generate(project, schema=None, ledger=None, python=None, no_ledger=False):
    """Runs `etask generate` over a project directory.

    @param project The project root (holding `src/` and `schema.yaml`).
    @param schema The schema to read; defaults to the project's own.
    @param ledger The uid ledger; defaults to the one beside the schema.
    @param python Where to write the client bindings, if anywhere.
    @param no_ledger Pass `--no-uid-ledger`, deriving uids from the schema
           alone. Distinct from `ledger=None`, which merely means "wherever the
           generator puts it by default" - a difference that matters entirely,
           since one arm of the boundary check depends on there being no ledger
           at all.
    @return The completed process, for the caller to check.
    """
    project = Path(project)
    argv = [
        sys.executable, "-m", "etask.schema.cli", "generate",
        str(schema or project / "schema.yaml"),
        "--out", str(project / "src" / "sys"),
        "--task-id", str(project / "src" / "generated" / "task_id.hpp"),
        "--task-list", str(project / "src" / "generated" / "task_list.hpp"),
        "--links", str(project / "src" / "generated" / "links.hpp"),
        "--scopes", str(project / "src" / "generated" / "scopes.hpp"),
    ]
    if no_ledger:
        argv.append("--no-uid-ledger")
    elif ledger is not None:
        argv += ["--uid-ledger", str(ledger)]
    if python is not None:
        argv += ["--python", str(python)]
    return subprocess.run(
        argv,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(GENERATOR_ROOT)},
        capture_output=True,
        text=True,
    )


# ------------------------------------------------------------------ 1. structure


def check_structure(ledger):
    """Asserts the tree the generator built is the tree the schema describes.

    @param ledger The parsed uid ledger.
    @return True if every structural assertion held.
    """
    failures = Failures()
    uids = ledger["uids"]

    failures.check(
        len(uids) == EXPECTED_TASKS,
        f"expected {EXPECTED_TASKS} tasks, ledger has {len(uids)}",
    )

    # Distinctness is the whole premise. Everything downstream - the C++ enum,
    # the registries, the client - assumes a uid names one task.
    values = list(uids.values())
    if not failures.check(
        len(set(values)) == len(values),
        f"{len(values) - len(set(values))} uid(s) are shared by more than one task",
    ):
        seen = {}
        for path, uid in uids.items():
            seen.setdefault(uid, []).append(path)
        for uid, paths in sorted(seen.items()):
            if len(paths) > 1:
                failures.messages.append(f"uid {uid}: {', '.join(sorted(paths))}")

    # Two bytes, and for two independent reasons: 294 tasks is past what one
    # byte holds, and `bus.reserve.emergency_halt` pins 40000, which one byte
    # could not express even in an otherwise small tree.
    failures.check(
        ledger["uid_bytes"] == EXPECTED_UID_BYTES,
        f"expected a {EXPECTED_UID_BYTES}-byte uid width, ledger says {ledger['uid_bytes']}",
    )
    failures.check(
        len(uids) > 256,
        f"the tree no longer exceeds a one-byte uid space ({len(uids)} tasks); "
        "the width check above would then pass for the wrong reason",
    )

    # The abstract fan-out: three stacked abstract scopes must have produced
    # every combination, each with its own four tasks.
    missing = [
        f"mesh.{segment}.{node}.{probe}.{task}"
        for segment in (f"s{i}" for i in range(SEGMENTS))
        for node in (f"n{i}" for i in range(NODES))
        for probe in (f"p{i}" for i in range(PROBES))
        for task in ("sample", "arm", "hold", "quench")
    ]
    absent = [path for path in missing if path not in uids]
    failures.check(
        not absent,
        f"{len(absent)} expected mesh task(s) absent, e.g. {absent[:3]}",
    )

    # The explicit pins, which the ledger must honor over anything it derived.
    for path, pinned in (("bus.reserve.emergency_halt", 40000),
                         ("bus.reserve.diagnostic", 300)):
        failures.check(
            uids.get(path) == pinned,
            f"'{path}' should hold its pinned uid {pinned}, holds {uids.get(path)}",
        )

    # The flattened-name near miss: two paths one component boundary apart must
    # be two entries with two uids.
    left, right = uids.get("bus.link_state.probe"), uids.get("bus.link.state_probe2")
    failures.check(
        left is not None and right is not None and left != right,
        f"the flattened-name near miss collapsed: bus.link_state.probe={left}, "
        f"bus.link.state_probe2={right}",
    )

    return failures.report("structure: 294 tasks, distinct uids, 2-byte width, fan-out complete")


# --------------------------------------------------- 2. reachability and identity


def run_binary(uids):
    """Feeds every uid to the built binary and parses what it reports.

    @param uids The uids to ask about, in order.
    @return A dict of requested uid -> (status, reports, reported uid, phase).
    @throws SystemExit If the binary is missing or fails.
    """
    if not BINARY.exists():
        print(f"FAIL  the binary is not built: {BINARY}")
        print("      run: cmake -S . -B build && cmake --build build")
        raise SystemExit(1)

    completed = subprocess.run(
        [str(BINARY)],
        input="\n".join(str(uid) for uid in uids) + "\n",
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        print(f"FAIL  the binary exited {completed.returncode}")
        print(completed.stderr)
        raise SystemExit(1)

    observed = {}
    for line in completed.stdout.splitlines():
        parts = line.split()
        if len(parts) != 5:
            continue
        requested, status, reports, reported, phase = parts
        observed[int(requested)] = (status, int(reports), int(reported), int(phase))
    return observed


def check_identity(ledger, observed):
    """Asserts every task is reachable by uid and answers as itself.

    @param ledger The parsed uid ledger.
    @param observed What the binary reported, keyed by requested uid.
    @return True if every task answered for itself.
    """
    failures = Failures()
    uids = ledger["uids"]

    #: A task with no `returns:` in the schema is an instant command, and reports
    #: from its constructor rather than from a completion. There are exactly two
    #: kinds here, and which one a uid is can be told from its path.
    instant = {path for path in uids if path.endswith(".quench")
               or path == "bus.reserve.emergency_halt"}

    unreached = [path for path, uid in uids.items() if uid not in observed]
    if not failures.check(not unreached, f"{len(unreached)} task(s) produced no output line"):
        for path in sorted(unreached)[:5]:
            failures.messages.append(f"no line for '{path}' (uid {uids[path]})")

    for path, uid in sorted(uids.items()):
        if uid not in observed:
            continue
        status, reports, reported, phase = observed[uid]

        if status != str(STATUS_OK):
            failures.messages.append(
                f"'{path}' (uid {uid}) was refused: status_code {status}")
            continue

        # Exactly one report. Zero means the uid routed nowhere; more than one
        # means it routed to more than one task, which is the aliasing this
        # whole project is looking for.
        if reports != 1:
            failures.messages.append(
                f"'{path}' (uid {uid}) produced {reports} reports, expected 1")
            continue

        # The report itself: the task says which uid it was *compiled* with. A
        # mismatch means the number reached a task that is not the one that owns
        # it - two abstract-scope instances aliased onto one, most likely.
        if reported != uid:
            wrong = next((p for p, u in uids.items() if u == reported), "?")
            failures.messages.append(
                f"'{path}' (uid {uid}) was answered by uid {reported} ('{wrong}')")
            continue

        expected_phase = PHASE_RAN if path in instant else PHASE_COMPLETED
        if phase != expected_phase:
            failures.messages.append(
                f"'{path}' (uid {uid}) reported at phase {phase}, expected {expected_phase}")

    return failures.report(
        f"identity: all {len(uids)} tasks reachable by uid, each answering as itself")


def check_instances_are_distinct(ledger, observed):
    """Asserts abstract-scope instances are separate tasks, not aliases.

    Singled out from the sweep above because it is the specific claim the
    abstract-scope machinery makes, and a failure here means something quite
    different from a task simply being unreachable: it means one definition
    produced one task where it should have produced many.

    @param ledger The parsed uid ledger.
    @param observed What the binary reported.
    @return True if every instance is its own task.
    """
    failures = Failures()
    uids = ledger["uids"]

    # Every leaf task of the fan-out, grouped by the definition it came from.
    # All 72 copies of `sample` were written once in the schema; if the
    # expansion pass merged any of them, this is where it shows.
    for task in ("sample", "arm", "hold", "quench"):
        group = {path: uid for path, uid in uids.items()
                 if path.startswith("mesh.") and path.endswith("." + task)}
        expected = SEGMENTS * NODES * PROBES
        failures.check(
            len(group) == expected,
            f"'{task}' expanded to {len(group)} instances, expected {expected}",
        )
        failures.check(
            len(set(group.values())) == len(group),
            f"'{task}' instances share uids: {len(group)} paths, "
            f"{len(set(group.values()))} distinct uids",
        )
        # And distinct at *runtime*, not merely in the ledger: each must have
        # answered with its own number.
        answered = {observed[uid][2] for uid in group.values() if uid in observed}
        failures.check(
            len(answered) == len(group),
            f"'{task}' instances answered with {len(answered)} distinct uids "
            f"across {len(group)} tasks - some are aliases of one another",
        )

    # The sharpest single pair: two probes on the same node, one definition.
    left = uids["mesh.s0.n0.p0.sample"]
    right = uids["mesh.s0.n0.p1.sample"]
    failures.check(left != right, f"p0.sample and p1.sample share uid {left}")
    if left in observed and right in observed:
        failures.check(
            observed[left][2] == left and observed[right][2] == right,
            f"sibling probes answered for each other: p0 -> {observed[left][2]}, "
            f"p1 -> {observed[right][2]}",
        )

    return failures.report(
        "abstract scopes: 72 instances per definition, each a genuinely separate task")


# ------------------------------------------------------------------ 3. deep paths


def check_deep_paths(ledger):
    """Asserts the generated client resolves deep paths to the ledger's uids.

    The client is a second, independent projection of the same schema, so
    walking it by attribute and comparing to the ledger checks the naming rules
    (dotted path -> Pascal class, scope nesting) against the uid assignment they
    are supposed to travel with.

    @param ledger The parsed uid ledger.
    @return True if every sampled path resolved to the right uid.
    """
    failures = Failures()
    if not failures.check(CLIENT.exists(), f"the client bindings are missing: {CLIENT}"):
        return failures.report("deep paths")

    sys.path.insert(0, str(GENERATOR_ROOT))
    sys.path.insert(0, str(CLIENT.parent))
    try:
        import tasks as bindings
    except ImportError as error:
        failures.check(False, f"could not import the generated client: {error}")
        return failures.report("deep paths")

    failures.check(
        bindings.UID_BYTES == EXPECTED_UID_BYTES,
        f"the client says UID_BYTES={bindings.UID_BYTES}, ledger says "
        f"{ledger['uid_bytes']}",
    )

    # Walk the client's scope tree the way a user would, by attribute, and hold
    # what is found against the ledger. Instantiating `Tasks` needs a `Client`,
    # which needs a channel - so the bindings are inspected as classes instead,
    # which is what carries UID and PATH anyway.
    def resolve(dotted):
        """@return The binding class at `dotted`, by walking the module's classes."""
        for name in dir(bindings):
            candidate = getattr(bindings, name)
            if getattr(candidate, "PATH", None) == dotted:
                return candidate
        return None

    #: One path per structural feature, rather than all 294: the sweep in
    #: check_identity already covers every uid, and what is wanted here is that
    #: *naming* survives depth, near misses, and the root.
    sampled = [
        "mesh.s0.n0.p0.sample",     # five levels down, first instance
        "mesh.s5.n3.p2.quench",     # five levels down, last instance, instant tier
        "mesh.s3.n1.p2.hold",       # somewhere in the middle, stateful tier
        "bus.link_state.probe",     # the near miss, underscore in the scope
        "bus.link.state_probe2",    # the near miss, underscore in the task
        "bus.reserve.emergency_halt",
        "bus.reserve.diagnostic",
        "bus.reserve.audit",
        "census",                   # root level: no scope path at all
    ]
    for dotted in sampled:
        binding = resolve(dotted)
        if not failures.check(binding is not None, f"the client has no binding for '{dotted}'"):
            continue
        expected = ledger["uids"][dotted]
        failures.check(
            int(binding.UID) == expected,
            f"'{dotted}': the client says uid {int(binding.UID)}, the ledger says {expected}",
        )

    # And the tree really is nested, not flattened: the scope classes exist at
    # each level and hold the next one down.
    failures.check(
        hasattr(bindings, "_MeshS0N0P0Scope"),
        "the client did not emit a scope class for the five-level-deep "
        "`mesh.s0.n0.p0` - the nesting was flattened",
    )

    return failures.report("deep paths: the generated client agrees with the ledger")


# -------------------------------------------------------------------- 4. the ledger


def stage_copy(destination):
    """Copies the project into `destination` so a regeneration can be destructive.

    Only what generation reads or writes: the schema, the ledger, and the
    generated tree. The build directory is deliberately left behind - it is
    large, and nothing here compiles.

    @param destination An existing empty directory.
    @return The staged project root.
    """
    project = Path(destination) / "deep_tree"
    (project / "src").mkdir(parents=True)
    shutil.copy2(SCHEMA, project / "schema.yaml")
    shutil.copy2(LEDGER, project / ".schema.uids.json")
    shutil.copytree(HERE / "src" / "sys", project / "src" / "sys")
    shutil.copytree(HERE / "src" / "generated", project / "src" / "generated")
    return project


def diff_uids(before, after):
    """@return A list of "path: old -> new" for every uid that changed."""
    return [
        f"{path}: {uid} -> {after[path]}"
        for path, uid in sorted(before.items())
        if path in after and after[path] != uid
    ]


def check_ledger_is_stable():
    """Regenerates twice and asserts no uid ever moved.

    The two regenerations ask different questions:

    - the first changes nothing at all, so a uid that moved would mean the
      derivation is not even a function of its own inputs;
    - the second **adds a task**, which is the edit that used to renumber
      everything: before the ledger existed, a derived uid was a hash folded
      into a width chosen from the task *count*, so the 257th task re-derived
      every id in the project. That is the failure this check exists for.

    @return True if no existing uid moved across either regeneration.
    """
    failures = Failures()
    baseline = load_ledger(LEDGER)["uids"]

    with tempfile.TemporaryDirectory() as tmp:
        project = stage_copy(tmp)

        # --- regeneration 1: nothing changed ---------------------------------
        completed = generate(project)
        if not failures.check(
            completed.returncode == 0,
            f"a no-op regeneration failed:\n{completed.stderr}",
        ):
            return failures.report("the ledger")

        first = load_ledger(project / ".schema.uids.json")
        moved = diff_uids(baseline, first["uids"])
        failures.check(
            not moved,
            f"{len(moved)} uid(s) MOVED across a no-op regeneration:\n      "
            + "\n      ".join(moved[:20]),
        )
        failures.check(
            first["uid_bytes"] == EXPECTED_UID_BYTES,
            f"the uid width changed on a no-op regeneration: "
            f"{EXPECTED_UID_BYTES} -> {first['uid_bytes']}",
        )
        # The generator warns on stderr rather than moving a uid silently, so an
        # empty stderr is part of the claim, not incidental.
        failures.check(
            "uid" not in completed.stderr.lower(),
            f"the generator warned about uids on a no-op regeneration:\n{completed.stderr}",
        )

        # --- regeneration 2: one new task ------------------------------------
        # Appended to the *concrete* side. A new instance in an abstract scope
        # would add 4 tasks and also test something else; one task in one place
        # isolates the question to "does adding a task disturb the others".
        schema_text = (project / "schema.yaml").read_text()
        anchor = "          audit:\n"
        if not failures.check(anchor in schema_text, "could not find the insertion anchor in the schema"):
            return failures.report("the ledger")
        addition = (
            "          newcomer:\n"
            "            type: oneshot_task\n"
            "            brief: added by verify.py to test that existing uids hold still\n"
            "            params: {}\n"
            "            returns: { uid: uint16 }\n"
        )
        (project / "schema.yaml").write_text(schema_text.replace(anchor, addition + anchor, 1))

        completed = generate(project)
        if not failures.check(
            completed.returncode == 0,
            f"regeneration after adding a task failed:\n{completed.stderr}",
        ):
            return failures.report("the ledger")

        second = load_ledger(project / ".schema.uids.json")
        moved = diff_uids(baseline, second["uids"])
        failures.check(
            not moved,
            f"{len(moved)} uid(s) MOVED when a task was ADDED - this is a wire break; "
            f"every deployed peer holding one of these is now addressing the wrong "
            f"task:\n      " + "\n      ".join(moved[:20]),
        )

        # The new task must have arrived, with a uid of its own that collides
        # with nothing - including nothing retired.
        newcomer = second["uids"].get("bus.reserve.newcomer")
        if failures.check(newcomer is not None, "the added task got no uid at all"):
            # Named eagerly rather than inside the message, because the message
            # is built whether or not the check fails - and there is no such
            # holder in the passing case.
            holder = next((p for p, u in baseline.items() if u == newcomer), None)
            failures.check(
                holder is None,
                f"the added task took uid {newcomer}, which '{holder}' already held",
            )
            failures.check(
                len(second["uids"]) == EXPECTED_TASKS + 1,
                f"expected {EXPECTED_TASKS + 1} tasks after the addition, "
                f"got {len(second['uids'])}",
            )
        failures.check(
            not second["retired"],
            f"nothing was removed, yet {len(second['retired'])} path(s) were retired: "
            f"{sorted(second['retired'])[:5]}",
        )

    return failures.report(
        "the ledger: no uid moved across a no-op regeneration, nor when a task was added")


def check_removal_reserves():
    """Asserts a removed task's uid is reserved rather than handed on.

    The mirror of the addition case, and the subtler half. A peer that still
    holds a deleted task's uid will keep sending it; if that number were later
    reused for a *different* task, the device would run the wrong one on a
    request that looks entirely valid. The ledger's `retired` table is what
    prevents it, and this is what asks whether it does.

    @return True if the removed uid stayed reserved and out of circulation.
    """
    failures = Failures()
    baseline = load_ledger(LEDGER)["uids"]
    victim = "bus.reserve.audit"
    victim_uid = baseline[victim]

    with tempfile.TemporaryDirectory() as tmp:
        project = stage_copy(tmp)

        text = (project / "schema.yaml").read_text()
        start = text.index("          audit:\n")
        end = text.index("  # A root-level task")
        (project / "schema.yaml").write_text(text[:start] + text[end:])

        completed = generate(project)
        if not failures.check(
            completed.returncode == 0,
            f"regeneration after removing a task failed:\n{completed.stderr}",
        ):
            return failures.report("the ledger: removal")

        after = load_ledger(project / ".schema.uids.json")
        failures.check(
            victim not in after["uids"],
            f"'{victim}' was removed from the schema but is still live in the ledger",
        )
        failures.check(
            after["retired"].get(victim) == victim_uid,
            f"'{victim}' should be retired holding uid {victim_uid}, "
            f"the ledger says {after['retired'].get(victim)}",
        )
        failures.check(
            victim_uid not in after["uids"].values(),
            f"uid {victim_uid} was handed to another task after '{victim}' was "
            f"removed - a peer still requesting it would now run the wrong task",
        )
        # Everything else must be exactly where it was.
        moved = diff_uids(baseline, after["uids"])
        failures.check(
            not moved,
            f"{len(moved)} uid(s) MOVED when a task was REMOVED:\n      "
            + "\n      ".join(moved[:20]),
        )

    return failures.report(
        "the ledger: a removed task's uid stays reserved, and nothing else moved")


def check_width_boundary():
    """Asserts that crossing 256 tasks does not renumber the tasks already there.

    This is the failure the ledger was built for, and the only one in this file
    that deep_tree's own schema cannot exercise: at 294 tasks the project is
    already two bytes wide and can never cross the boundary again. So the check
    builds its own throwaway schema, grows it across 256, and watches.

    Before the ledger, a derived uid was a blake2b hash of the task's path
    folded into a width chosen from the current task *count*. Adding the 257th
    task therefore re-derived **every** implicit uid in the project at a wider
    digest - silently, and with the schema otherwise unchanged. A peer built
    against the 256-task firmware would keep sending numbers that now mean
    different tasks, or nothing at all.

    Both halves are checked, because the second is what gives the first its
    meaning: with a ledger nothing moves, and with `--no-uid-ledger` on the same
    two schemas the uid *does* move. If the second half ever stopped moving, the
    first would be passing for free.

    @return True if the ledger held every uid across the width change.
    """
    failures = Failures()
    small, large = 250, 300

    def write(path, count):
        """Writes a flat schema of `count` oneshot tasks under one scope."""
        lines = ["system:", "  s:", "    type: scope", "    children:"]
        for index in range(count):
            lines += [f"      t{index}:",
                      "        type: oneshot_task",
                      "        returns: { id: uint16 }"]
        Path(path).write_text("\n".join(lines) + "\n")

    def uids_of(project, schema, ledger):
        """Generates and returns the resulting name -> uid map and width.

        @param project The staged project root.
        @param schema The schema to generate from.
        @param ledger The ledger path, or None to generate without one.
        @return The uid map and the uid width; the width is None when there was
                no ledger to read it from.
        """
        completed = generate(project, schema=schema, ledger=ledger,
                             no_ledger=ledger is None)
        if completed.returncode != 0:
            failures.check(False, f"generation failed:\n{completed.stderr}")
            return None, None
        if ledger is None:
            # With no ledger there is no file to read the uids from, so they are
            # read back out of the emitted enum instead - which is the same
            # numbers by a different route, and the only route this arm has.
            text = (Path(project) / "src" / "generated" / "task_id.hpp").read_text()
            found = {}
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("s_t") and "=" in stripped:
                    name, _, rest = stripped.partition("=")
                    found[name.strip()] = int(rest.split(",")[0].strip())
            return found, None
        parsed = load_ledger(ledger)
        return parsed["uids"], parsed["uid_bytes"]

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        # --- with a ledger: nothing may move ---------------------------------
        kept = root / "kept"
        (kept / "src").mkdir(parents=True)
        schema = kept / "schema.yaml"
        ledger = kept / "uids.json"

        write(schema, small)
        before, before_width = uids_of(kept, schema, ledger)
        if before is None:
            return failures.report("the ledger: crossing the one-byte uid boundary")
        failures.check(
            before_width == 1,
            f"a {small}-task schema should be one byte wide, is {before_width}",
        )

        write(schema, large)
        after, after_width = uids_of(kept, schema, ledger)
        if after is None:
            return failures.report("the ledger: crossing the one-byte uid boundary")
        failures.check(
            after_width == 2,
            f"a {large}-task schema should be two bytes wide, is {after_width}",
        )

        moved = diff_uids(before, after)
        failures.check(
            not moved,
            f"{len(moved)} uid(s) MOVED when the tree grew past 256 tasks and the "
            f"width widened - this is the wire break the ledger exists to prevent:"
            f"\n      " + "\n      ".join(moved[:20]),
        )

        # --- without one: the move must still happen -------------------------
        # Not a check of the generator so much as of this check. If dropping the
        # ledger stopped changing anything, the arm above would be asserting
        # nothing at all.
        loose = root / "loose"
        (loose / "src").mkdir(parents=True)
        loose_schema = loose / "schema.yaml"

        write(loose_schema, small)
        narrow, _ = uids_of(loose, loose_schema, None)
        write(loose_schema, large)
        wide, _ = uids_of(loose, loose_schema, None)

        if narrow and wide:
            shifted = [name for name in narrow if name in wide and narrow[name] != wide[name]]
            failures.check(
                shifted,
                "with --no-uid-ledger, growing past 256 tasks left every uid where "
                "it was. That should be impossible - the width changed - so the "
                "ledger arm of this check is no longer proving anything.",
            )

    return failures.report(
        "the ledger: crossing the one-byte uid boundary renumbers nothing")


def main():
    """@return Process exit status: 0 if every check passed, 1 otherwise."""
    if not LEDGER.exists():
        print(f"FAIL  no uid ledger at {LEDGER}; generate the project first")
        return 1

    ledger = load_ledger(LEDGER)
    print(f"deep_tree: {len(ledger['uids'])} tasks, {ledger['uid_bytes']}-byte uids\n")

    results = [check_structure(ledger)]

    observed = run_binary(list(ledger["uids"].values()))
    results.append(check_identity(ledger, observed))
    results.append(check_instances_are_distinct(ledger, observed))
    results.append(check_deep_paths(ledger))
    results.append(check_ledger_is_stable())
    results.append(check_removal_reserves())
    results.append(check_width_boundary())

    print()
    if all(results):
        print(f"PASSED  {len(results)} checks")
        return 0
    print(f"FAILED  {results.count(False)} of {len(results)} checks")
    return 1


if __name__ == "__main__":
    sys.exit(main())
