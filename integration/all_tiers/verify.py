#!/usr/bin/env python3
"""Host-side driver for the ``all_tiers`` integration project.

Builds nothing and knows nothing about C++: it runs the conformance binary (or
reads a captured serial log), parses the ``etask <key>=<value>`` lines it prints,
and asserts the framework's documented lifecycle against them.

    python3 verify.py                      # build/all_tiers, the CMake default
    python3 verify.py --binary path/to/exe # a different host build
    python3 verify.py --log serial.txt     # what a board said, captured

Exits 0 when every expectation holds, 1 otherwise, printing expected against
actual for each failure.

## What it is asserting against

Every expectation here is written from the *documentation*, not from what the
firmware happens to do - the point of a conformance run is to disagree with the
implementation when the implementation is wrong. Each check names the file and
the claim it is holding the framework to, so a failure says which promise broke
rather than only which number moved.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

#: Manager/API and task status codes, from etask/core/status_code.hpp.
STATUS = {
    "ok": 0x00,
    "task_already_paused": 0x03,
    "task_already_resumed": 0x04,
    "task_already_running": 0x02,
    "invalid_completion_reason": 0x15,
    "task_not_pausable": 0x16,
    "task_not_addressable": 0x17,
    "task_finished": 0x20,
    "task_aborted": 0x21,
    "task_completed_early": 0x28,
}

#: Lifecycle hook bits, from support/lifecycle/recorder.hpp.
HOOK = {
    "construct": 0x01,
    "execute": 0x02,
    "pause": 0x04,
    "resume": 0x08,
    "finish": 0x10,
    "complete": 0x20,
}

#: The caller-supplied completion_reason the force-complete scenarios send.
#: completion_reason::user_defined_start, from etask/core/completion_reason.hpp.
USER_REASON_0 = 0x10

#: One reported observation: ``etask <key>=<value>``.
_LINE = re.compile(r"^etask\s+([A-Za-z0-9_.]+)=(\d+)\s*$")

#: The line the firmware prints once the whole run is over.
_DONE = "etask done"


class Report:
    """The observations a run produced, keyed by name."""

    def __init__(self, text: str):
        """Parses a run's output.

        Args:
            text: Everything the firmware printed. Lines that are not
                observations are ignored, so a board's boot chatter is harmless.
        """
        self.values: dict[str, int] = {}
        self.complete = False
        for line in text.splitlines():
            line = line.strip()
            if line == _DONE:
                self.complete = True
                continue
            match = _LINE.match(line)
            if match:
                self.values[match.group(1)] = int(match.group(2))

    def get(self, key: str) -> int | None:
        """One observation.

        Args:
            key: Its dotted name.

        Returns:
            The value, or ``None`` if the run never reported it.
        """
        return self.values.get(key)


class Checker:
    """Accumulates pass/fail verdicts and prints them as they are decided."""

    def __init__(self, report: Report):
        """Binds the checker to the report it reads from.

        Args:
            report: The parsed observations to assert against.
        """
        self._report = report
        self.failures: list[str] = []
        self._passes = 0

    def equals(self, key: str, expected: int, why: str, expected_name: str = "") -> None:
        """Asserts one observation equals what the documentation promises.

        Args:
            key: Dotted name of the observation.
            expected: The value the framework's own documentation calls for.
            why: What breaks if it does not hold - the claim being tested, and
                where it is written down.
            expected_name: Optional symbolic name for ``expected``, so a status
                code reads as more than a number.
        """
        actual = self._report.get(key)
        shown = f"{expected} ({expected_name})" if expected_name else str(expected)

        if actual is None:
            self.__fail(key, shown, "not reported", why)
        elif actual != expected:
            self.__fail(key, shown, str(actual), why)
        else:
            self._passes += 1
            print(f"  ok   {key} = {shown}")

    def hooks(self, key: str, expected: list[str], why: str) -> None:
        """Asserts exactly this set of lifecycle hooks fired.

        Checked as a whole rather than bit by bit: a hook that fired when it
        should not have is as much a fault as one that did not fire, and only
        comparing the full mask catches both.

        Args:
            key: Dotted name of the reported ``hooks`` bitmask.
            expected: Hook names, from ``HOOK``, that must all have fired and be
                the only ones that did.
            why: What breaks if it does not hold.
        """
        wanted = 0
        for name in expected:
            wanted |= HOOK[name]

        actual = self._report.get(key)
        if actual is None:
            self.__fail(key, self.__names(wanted), "not reported", why)
            return

        if actual != wanted:
            self.__fail(key, self.__names(wanted), self.__names(actual), why)
        else:
            self._passes += 1
            print(f"  ok   {key} = {self.__names(wanted)}")

    @staticmethod
    def __names(mask: int) -> str:
        """Renders a hook mask as names, so a diff is readable.

        Args:
            mask: The bitmask.

        Returns:
            The hook names present, ``|``-joined, with the raw value.
        """
        present = [name for name, bit in HOOK.items() if mask & bit]
        return f"{'|'.join(present) or '<none>'} ({mask})"

    def __fail(self, key: str, expected: str, actual: str, why: str) -> None:
        """Records and prints one failure.

        Args:
            key: What was being checked.
            expected: The documented value, rendered.
            actual: What the run actually reported, rendered.
            why: The claim that broke.
        """
        self.failures.append(key)
        print(f"  FAIL {key}")
        print(f"       expected: {expected}")
        print(f"       actual:   {actual}")
        print(f"       why:      {why}")

    def summary(self) -> int:
        """Prints the tally.

        Returns:
            0 if everything held, 1 otherwise - the process exit status.
        """
        total = self._passes + len(self.failures)
        print()
        if self.failures:
            print(f"FAILED: {len(self.failures)} of {total} checks")
            for key in self.failures:
                print(f"  - {key}")
            return 1
        print(f"PASSED: all {total} checks")
        return 0


class Scenarios:
    """The documented lifecycle, expressed as assertions over a report."""

    def __init__(self, checker: Checker):
        """Binds the scenarios to the checker they report through.

        Args:
            checker: Where verdicts are accumulated.
        """
        self._check = checker

    def run_all(self) -> None:
        """Runs every scenario's assertions, in the order the firmware ran them."""
        self.instant_tier()
        self.oneshot_tier()
        self.polled_tier()
        self.force_completion()
        self.repeated_directives()
        self.stateful_tier()
        self.suspension_is_honored()

    def instant_tier(self) -> None:
        """An instant command runs on arrival, replies nothing, and is unaddressable."""
        print("\ninstant_task: runs on arrival, sends no reply")
        self._check.equals(
            "instant.register", STATUS["ok"],
            "instant_task.hpp: the command runs to completion inside the call "
            "that delivers it, so registering it must succeed outright.",
            "ok")
        self._check.equals(
            "instant.arrivals", 1,
            "instant_task.hpp: 'the constructor is the whole task' - it must "
            "have run before register_task returned, with no tick given.")
        self._check.equals(
            "instant.completions", 0,
            "instant_task.hpp: 'No reply reaches the requester - not even a "
            "success status.'")
        self._check.equals(
            "instant.completions_after_tick", 0,
            "instant_task.hpp: it 'never enters the manager's storage, never "
            "sees an update() tick', so a tick cannot produce a late reply.")

        print("\ninstant_task: every directive aimed at its uid is refused")
        for op in ("pause", "resume", "complete"):
            self._check.equals(
                f"instant.{op}", STATUS["task_not_addressable"],
                "task_manager.hpp: 'Pause, resume, and complete all address a "
                "live task. An instant_task is never live', so all three are "
                "answered task_not_addressable - not task_not_registered.",
                "task_not_addressable")

    def oneshot_tier(self) -> None:
        """A oneshot runs exactly one execution step, then answers."""
        print("\noneshot_task: runs once and answers")
        self._check.equals(
            "oneshot.register", STATUS["ok"],
            "The task is in the polled tier and the budget is free.",
            "ok")
        self._check.equals(
            "oneshot.completions", 1,
            "oneshot_task.hpp: unlike an instant command, this tier exists "
            "precisely because 'producing a reply requires a completion'.")
        self._check.equals(
            "oneshot.status", STATUS["task_finished"],
            "It reached its own end, so the manager's natural-completion status "
            "stands.",
            "task_finished")
        self._check.equals(
            "oneshot.f1", 1,
            "oneshot_task.hpp: 'on_execute() - the task's whole job, run once.' "
            "Exactly one execution, no matter how many ticks are given.")
        self._check.hooks(
            "oneshot.f0", ["construct", "execute", "complete"],
            "oneshot_task.hpp lifecycle: 'on_execute() ... then on_complete(), "
            "once, immediately after.'")

    def polled_tier(self) -> None:
        """A polled task runs across ticks, decides its own end, and cannot suspend."""
        print("\npolled_task: runs across ticks and decides its own completion")
        self._check.equals(
            "polled.register", STATUS["ok"], "The budget is free.", "ok")
        self._check.equals(
            "polled.completions_before_conclusion", 0,
            "polled_task.hpp: the manager 'asks is_finished() whether to keep "
            "going' - a task still working must not have been concluded.")
        self._check.equals(
            "polled.completions", 1, "It concludes exactly once, at the end.")
        self._check.equals(
            "polled.status", STATUS["task_finished"],
            "It decided its own end, which is a natural completion.",
            "task_finished")
        self._check.equals(
            "polled.f1", 3,
            "polled_task.hpp: 'on_execute() - one slice of work, every tick, "
            "until finished.' It asked for three slices and must get three.")
        self._check.hooks(
            "polled.f0", ["construct", "execute", "finish", "complete"],
            "polled_task.hpp: both hooks are polled, then on_complete() runs. "
            "No pause or resume - this tier does not have them.")

        print("\npolled_task: pause and resume are refused")
        for op in ("pause", "resume"):
            self._check.equals(
                f"polled_ns.{op}", STATUS["task_not_pausable"],
                "stateful_task.hpp: 'This is the only tier the manager will "
                "accept a pause or resume directive for. Aimed at any other "
                "tier, those directives are answered task_not_pausable.' The "
                "task is live when asked, so this is about the tier.",
                "task_not_pausable")

    def force_completion(self) -> None:
        """A forced ending: refused for `finished`, and carrying the caller's reason."""
        print("\ncomplete_task: completion_reason::finished is refused")
        self._check.equals(
            "refuse.complete_finished", STATUS["invalid_completion_reason"],
            "completion_reason.hpp: finished is 'Framework-only; never pass "
            "this to complete_task' - it names an ending the caller did not "
            "cause.",
            "invalid_completion_reason")

        print("\ncomplete_task: a forced ending reports early, and the reason arrives")
        self._check.equals(
            "force.complete", STATUS["ok"],
            "A live, unfinished task accepts a caller-supplied reason.", "ok")
        self._check.equals(
            "force.status", STATUS["task_completed_early"],
            "status_code.hpp: task_completed_early is 'force-completed for a "
            "caller-supplied reason: it concluded before it would have on its "
            "own, but was not aborted.'",
            "task_completed_early")
        self._check.equals(
            "force.f2", USER_REASON_0,
            "task.hpp: on_complete takes 'a caller-supplied reason for a "
            "forced one'. The task echoes the byte it was handed, so this "
            "proves the caller's reason reached the hook unflattened.")
        self._check.hooks(
            "force.f0", ["construct", "execute", "finish", "complete"],
            "The task ran normally until it was ended from outside; being "
            "force-completed does not skip on_complete().")

    def repeated_directives(self) -> None:
        """A second pause and a second resume are each rejected in kind."""
        print("\nstateful_task: repeated directives are rejected")
        self._check.equals(
            "stateful.register", STATUS["ok"], "The stateful budget is free.", "ok")
        self._check.equals(
            "dbl.pause_first", STATUS["ok"],
            "A running stateful task accepts a pause.", "ok")
        self._check.equals(
            "dbl.pause_second", STATUS["task_already_paused"],
            "stateful_task_manager: 'Suspended, or already on its way there: "
            "nothing further to ask for.'",
            "task_already_paused")
        self._check.equals(
            "dbl.resume_first", STATUS["ok"],
            "A suspended task accepts a resume.", "ok")
        self._check.equals(
            "dbl.resume_second", STATUS["task_already_resumed"],
            "status_code.hpp: task_already_resumed is 'Resume requested but "
            "task already marked resumed' - a resume is already pending.",
            "task_already_resumed")

    def stateful_tier(self) -> None:
        """A stateful task pauses, resumes, and finishes, with both hooks firing."""
        print("\nstateful_task: pauses, resumes, and finishes")
        self._check.equals(
            "stateful.completions", 1, "It concludes exactly once.")
        self._check.equals(
            "stateful.status", STATUS["task_finished"],
            "It reached its own end after the pause/resume round trip.",
            "task_finished")
        self._check.equals(
            "stateful.f3", 1,
            "stateful_task.hpp: 'on_pause() - once, when the task is paused.' "
            "The hook is pure virtual, so the compiler proves it exists; only "
            "this proves the manager calls it.")
        self._check.equals(
            "stateful.f4", 1,
            "stateful_task.hpp: 'on_resume() - once, when it resumes.'")
        self._check.equals(
            "stateful.f1", 2,
            "The suspension delays the work rather than cancelling it: both "
            "requested executions still happen.")
        self._check.hooks(
            "stateful.f0",
            ["construct", "execute", "pause", "resume", "finish", "complete"],
            "stateful_task.hpp lifecycle: every hook of the tier fires across a "
            "pause/resume round trip ending in a natural completion.")

    def suspension_is_honored(self) -> None:
        """A suspended task is not executed while it is suspended."""
        print("\nstateful_task: a paused task stays paused")
        self._check.equals(
            "held.pause", STATUS["ok"], "A running task accepts a pause.", "ok")
        self._check.equals(
            "held.f3", 1, "on_pause() fired once for the one pause requested.")
        self._check.equals(
            "held.f4", 0,
            "on_resume() must not fire: this task was never resumed.")

        executions = self._check._report.get("held.f1")
        at_pause = self._check._report.get("held.f2")
        self._check.equals(
            "held.f1", at_pause if at_pause is not None else -1,
            "stateful_task.hpp: 'While paused, on_execute() is not called; the "
            "task is idle until resumed or completed.' Four ticks passed "
            "suspended, so the total must still equal the count latched at "
            f"on_pause() ({at_pause}).")
        if executions is not None and at_pause is not None and executions > at_pause:
            print(f"       note: executed {executions - at_pause} time(s) while suspended")

        print("\ncomplete_task: a suspended task can still be concluded")
        self._check.equals(
            "held.complete", STATUS["ok"],
            "stateful_task_manager: 'Concluding is not gated on the run state: "
            "a suspended task may be completed exactly as a running one may.'",
            "ok")
        self._check.equals(
            "held.status", STATUS["task_completed_early"],
            "It was force-completed for a caller-supplied reason.",
            "task_completed_early")
        self._check.equals(
            "held.f5", USER_REASON_0,
            "The caller's reason reaches on_complete even when the task was "
            "suspended at the time.")


def _capture(binary: Path) -> str:
    """Runs the conformance binary and returns everything it printed.

    Args:
        binary: The executable to run.

    Returns:
        Its stdout, with stderr folded in so a crash message is not lost.

    Raises:
        SystemExit: If the binary is missing or cannot be run.
    """
    if not binary.exists():
        sys.exit(
            f"verify: no binary at {binary}\n"
            "        build it first:\n"
            "          cmake -S . -B build && cmake --build build"
        )

    try:
        completed = subprocess.run(
            [str(binary)], capture_output=True, text=True, timeout=60
        )
    except subprocess.TimeoutExpired:
        sys.exit(
            "verify: the binary did not finish within 60s.\n"
            "        The scenarios drive update() a fixed number of times and "
            "return, so a hang means a task never concluded."
        )

    if completed.returncode != 0:
        print(
            f"verify: the binary exited {completed.returncode}; "
            "checking what it managed to report first.",
            file=sys.stderr,
        )
    return completed.stdout + completed.stderr


def _main() -> int:
    """Parses arguments, obtains a report, and checks it.

    Returns:
        The process exit status: 0 if every expectation held.
    """
    parser = argparse.ArgumentParser(
        description="Assert the etask lifecycle against an all_tiers run."
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--binary", type=Path, default=Path(__file__).parent / "build" / "all_tiers",
        help="the host conformance binary to run (default: build/all_tiers)",
    )
    source.add_argument(
        "--log", type=Path, default=None,
        help="a captured serial log to check instead of running a binary",
    )
    args = parser.parse_args()

    if args.log is not None:
        if not args.log.exists():
            sys.exit(f"verify: no log at {args.log}")
        text = args.log.read_text()
        print(f"verify: checking captured log {args.log}")
    else:
        text = _capture(args.binary)
        print(f"verify: checking {args.binary}")

    report = Report(text)
    if not report.values:
        sys.exit(
            "verify: the run reported nothing at all.\n"
            "        Expected lines of the form 'etask <key>=<value>'."
        )

    checker = Checker(report)
    Scenarios(checker).run_all()

    if not report.complete:
        print()
        print("  FAIL report.complete")
        print("       expected: the run to end with 'etask done'")
        print("       actual:   the report stopped early")
        print("       why:      a truncated report means the firmware stopped "
              "partway, so the checks above covered only what it reached.")
        checker.failures.append("report.complete")

    return checker.summary()


if __name__ == "__main__":
    sys.exit(_main())
