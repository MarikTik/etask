#!/usr/bin/env python3
"""Builds and runs the bombardment harness, and judges what it reported.

Usage::

    python3 verify.py                 # configure, build, run, judge
    python3 verify.py --no-build      # judge an already-built binary
    python3 verify.py --build-dir b    # use another build directory

Exits 0 only if every expected check ran and passed. Anything else - a check
that failed, a check that never reported, a binary that crashed - is non-zero,
with the transcript and an explanation of what was expected printed first.

## What is being proved, and why a Python driver at all

The assertions themselves are in ``src/app.cpp``, because only C++ can call the
task manager: there is no wire link here, no serial port, nothing a Python
process could register a task through. So the harness checks, and this driver's
job is the part the harness cannot do for itself -

- **insisting every check ran.** A harness that returns 0 because it silently
  stopped after two checks looks identical, from the exit status, to one that
  passed all eight. :data:`EXPECTED_CHECKS` is the list it is held to, so a
  check deleted or short-circuited is a failure rather than an absence.
- **cross-checking the summary against the transcript.** The harness prints both
  a per-check verdict and a final count; if they disagree, its own bookkeeping is
  wrong and neither number can be trusted.
- **explaining the failure.** :data:`CHECK_INTENT` says what each check was for,
  so a failure names the framework claim that broke rather than only the check
  that noticed.

## The one place behaviour and documentation disagree

``single_instance_refusal`` expects ``duplicate_task`` (0x13), not
``task_limit_reached`` (0x12), and that is the framework's real behaviour rather
than a preference of this test.

``task_limit_reached``'s documentation says it means "this task type's own
concurrency cap is reached: every slot its ``capacity<Task, N>`` reserves is
occupied". A uid with no ``concurrency:`` in the schema reserves exactly one
slot, and one live instance occupies it - so by that wording the second
registration should be 0x12. The manager instead answers 0x13 whenever the cap
happens to be 1::

    if (running_count >= max_concurrent)
        return max_concurrent > 1 ? status_code::task_limit_reached
                                  : status_code::duplicate_task;

The check pins the behaviour that exists, so a change to it is noticed. Whether
the code or the documentation should move is a decision for the framework and
not for this test - but note that it is not cosmetic: 0x13 is documented as
"duplicate instance disallowed by policy", which describes a *rule against*
running two, while what actually happened is that the one slot allowed was in
use. A caller distinguishing the two - retry later, versus never - is told the
wrong thing.

## A second observation, encoded in the schema rather than in a check

The manager tests the per-uid cap before the tier's::

    if (running_count >= max_concurrent) return ...;   // 0x12 / 0x13
    if (_tasks.full())                   return status_code::task_budget_exhausted;

So when both are spent at the same registration, the per-uid answer wins, and a
uid whose ``concurrency`` equals its tier's ``budget`` can never produce 0x18 at
all - it reports 0x12 for a condition that is genuinely the tier's. The ordering
is defensible (the narrower cause is the more specific answer), but it means the
two codes are not always distinguishable at the point of refusal. This project
sidesteps it by keeping every uid strictly narrower than the budget; see the
note at the top of schema.yaml.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

#: This project's directory. Everything else is resolved relative to it, so the
#: driver works from any working directory - CI rarely runs it from here.
PROJECT_DIR = Path(__file__).resolve().parent

#: The etask checkout to build against: the one containing this test.
#:
#: Deliberately not a released tag. This project exists to test the headers
#: sitting next to it, and fetching a published etask instead would make it pass
#: or fail on code the developer is not editing.
ETASK_ROOT = PROJECT_DIR.parent.parent

#: Every check the harness must report, and what each one is for.
#:
#: The values are printed when a check fails or goes missing, so the reader is
#: told which framework claim is in question rather than only which function
#: name stopped saying PASS.
CHECK_INTENT = {
    "fill_to_budget":
        "a tier accepts exactly `budget` concurrent tasks, and they really occupy records",
    "budget_exhausted":
        "one past the budget is refused with task_budget_exhausted (0x18) - for every uid, "
        "including ones with slots of their own still free",
    "limit_reached_with_room":
        "saturating one uid while the tier still has room is task_limit_reached (0x12), and "
        "the tier really does still have room",
    "single_instance_refusal":
        "a uid with the default concurrency of 1 answers duplicate_task (0x13) when saturated "
        "- see this file's module docstring; the manager and task_limit_reached's "
        "documentation disagree here",
    "slots_reclaimed":
        "records are returned when tasks conclude, so registration succeeds again - the check "
        "that catches a leaked record",
    "stateful_tier_is_separate":
        "the stateful tier has its own budget: exhausting the polled tier does not touch it, "
        "and an instant command still runs with both full",
    "paused_task_holds_its_record":
        "a paused stateful task still occupies its record, so the tier does not gain capacity "
        "by suspending work",
    "sustained_churn":
        "thousands of register/complete cycles leave the manager behaving exactly as it did on "
        "the first check, with every constructed task also concluded",
}

#: Order the checks are expected in. The harness runs them in this order, and a
#: reordering is worth noticing: several checks depend on the manager being empty
#: when they start, which the one before them is responsible for leaving it.
EXPECTED_CHECKS = tuple(CHECK_INTENT)

#: `CHECK <name> <PASS|FAIL>` - one per check, the harness's per-check verdict.
CHECK_LINE = re.compile(r"^CHECK (\w+) (PASS|FAIL)$")

#: `BOMBARDMENT done failures=<n>` - the harness's own summary, cross-checked
#: against the verdicts so a disagreement between the two is itself a failure.
SUMMARY_LINE = re.compile(r"^BOMBARDMENT done failures=(\d+)$")


def build(build_dir: Path) -> None:
    """Configures and builds the harness, exiting non-zero if either step fails.

    @param build_dir Where CMake should put its build tree.
    """
    configure = [
        "cmake", "-S", str(PROJECT_DIR), "-B", str(build_dir),
        f"-DETASK_ROOT={ETASK_ROOT}",
    ]
    compile_ = ["cmake", "--build", str(build_dir), "-j"]

    for command in (configure, compile_):
        print(f"$ {' '.join(command)}", flush=True)
        completed = subprocess.run(command)
        if completed.returncode != 0:
            # No transcript to explain: a build failure has already printed its
            # own diagnosis, and adding to it only buries the compiler's message.
            sys.exit(
                f"verify: {command[0]} failed with status {completed.returncode}; "
                "the harness was not run."
            )


def run(binary: Path) -> "tuple[int, str]":
    """Runs the harness and returns what it said.

    Not checked for a zero status here: a non-zero exit is expected when a check
    fails, and the transcript is what says which. A *crash* is caught by the
    caller instead, where the missing checks make it obvious what happened.

    @param binary The harness executable.
    @return Its exit status and its combined stdout/stderr.
    """
    if not binary.exists():
        sys.exit(
            f"verify: no harness at {binary}.\n"
            "        Build it first, or drop --no-build."
        )
    completed = subprocess.run([str(binary)], capture_output=True, text=True)
    return completed.returncode, completed.stdout + completed.stderr


def judge(status: int, transcript: str) -> int:
    """Decides whether the run proved what it was supposed to.

    Three separate ways to fail, kept separate on purpose: a check that reported
    FAIL, a check that never reported at all, and a harness whose own summary
    disagrees with the verdicts it printed. The second is the one a naive driver
    misses - a harness that stops early exits 0.

    @param status     The harness's exit status.
    @param transcript Everything it printed.
    @return A process exit status: 0 if the run proved its claims.
    """
    verdicts = {}
    order = []
    for line in transcript.splitlines():
        match = CHECK_LINE.match(line)
        if match:
            verdicts[match.group(1)] = match.group(2)
            order.append(match.group(1))

    summary = None
    for line in transcript.splitlines():
        match = SUMMARY_LINE.match(line)
        if match:
            summary = int(match.group(1))

    problems = []

    failed = [name for name in EXPECTED_CHECKS if verdicts.get(name) == "FAIL"]
    for name in failed:
        problems.append(f"check {name} FAILED - it was proving that {CHECK_INTENT[name]}")

    missing = [name for name in EXPECTED_CHECKS if name not in verdicts]
    for name in missing:
        problems.append(
            f"check {name} never reported - expected a `CHECK {name} PASS` line. "
            f"It was proving that {CHECK_INTENT[name]}"
        )

    unexpected = [name for name in verdicts if name not in CHECK_INTENT]
    for name in unexpected:
        problems.append(
            f"check {name} reported but is not in EXPECTED_CHECKS - add it there with a note "
            "on what it proves, so a later regression in it is not silently tolerated"
        )

    if order != [name for name in EXPECTED_CHECKS if name in verdicts]:
        problems.append(
            f"checks ran out of order: expected {list(EXPECTED_CHECKS)}, got {order}. "
            "Several checks assume the managers are empty when they start, which the "
            "preceding check is what leaves them"
        )

    if summary is None:
        problems.append(
            "the harness printed no `BOMBARDMENT done failures=<n>` summary - it did not "
            "reach the end of setup(), so it probably crashed part-way through"
        )
    elif summary != len(failed):
        problems.append(
            f"the harness's own summary disagrees with its transcript: it reported "
            f"failures={summary} but printed {len(failed)} FAIL verdict(s). Its bookkeeping "
            "is wrong, so neither number can be trusted"
        )
    elif status != summary:
        problems.append(
            f"the harness exited {status} but summarized failures={summary}; main() is "
            "expected to return the failure count"
        )

    print(transcript, end="" if transcript.endswith("\n") else "\n")

    if not problems:
        print(f"verify: PASS - all {len(EXPECTED_CHECKS)} checks reported and passed.")
        return 0

    print()
    print(f"verify: FAIL - {len(problems)} problem(s):")
    for problem in problems:
        print(f"  - {problem}")
    return 1


def main() -> int:
    """Entry point.

    @return A process exit status: 0 if the framework behaved as documented.
    """
    parser = argparse.ArgumentParser(
        description="Build and run the etask bombardment harness, and judge its transcript.",
    )
    parser.add_argument(
        "--build-dir", type=Path, default=PROJECT_DIR / "build",
        help="CMake build directory (default: ./build)",
    )
    parser.add_argument(
        "--no-build", action="store_true",
        help="run the existing binary without configuring or compiling first",
    )
    args = parser.parse_args()

    build_dir = args.build_dir if args.build_dir.is_absolute() else Path.cwd() / args.build_dir
    if not args.no_build:
        build(build_dir)

    status, transcript = run(build_dir / "bombardment")
    return judge(status, transcript)


if __name__ == "__main__":
    sys.exit(main())
