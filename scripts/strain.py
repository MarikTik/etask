#!/usr/bin/env python3
"""Compile-time strain test: how large a schema can etask actually build?

Generates a project at each task count, compiles the one translation unit that
instantiates the task manager, and records time, peak memory and the size of
what was emitted. Answers two questions a user has at design time - "will a tree
this size build on my machine, and how long will I wait" - that nothing else in
the repository answers.

This measures **compile time only**. Runtime cost is a separate exercise
(`bench/runtime`); a schema that builds is not thereby fast.

Usage:
    scripts/strain.py                       # the default ladder
    scripts/strain.py --counts 500 1000     # specific points
    scripts/strain.py --resume              # skip points already in the log
    scripts/strain.py --compiler clang++    # cross-check another front end

## Safety

**This script is deliberately incapable of running two compilers at once.** The
machine it was written for has 8 cores and ~5 GB of real headroom, and a
parallel build of a large schema has taken its owner's editor down with it three
times. Every compile here is serial, and every one runs under an address-space
cap (`--cap-mb`, default 3000) so an over-run dies as a clean failure rather than
inviting the OOM killer.

Before each point the harness checks free memory and stops the ladder if it is
below `--min-free-mb`. It also stops on the first failure, since the ladder is
monotonic: if N does not build, N+1 will not either.

Results are appended to the log after **each** point, so an interrupted run keeps
everything it measured. `--resume` picks up from there.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import resource
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent
ELIB = REPO.parent

#: Task counts to measure. Geometric, so each point roughly doubles the cost of
#: the last - a linear ladder spends all its time at the top and tells you
#: nothing new on the way there.
DEFAULT_COUNTS = [100, 200, 400, 800, 1200, 1600, 2400, 3200]

#: The translation unit under test: it names the manager and constructs one.
#: Constructing it is the point - naming the type alone costs almost nothing,
#: and it is the constructor that instantiates the factory over the whole pack.
PROBE = """\
#include "generated/task_list.hpp"
#include <etask/core/managers/task_manager.hpp>

using manager_t = etask::core::managers::task_manager_from_t<
    generated::instant_tasks,
    generated::polled_tasks,
    generated::stateful_tasks,
    generated::polled_budget,
    generated::stateful_budget>;

manager_t manager{};

int main() { return 0; }
"""


def schema_for(count: int, per_scope: int = 10) -> str:
    """A schema of `count` polled tasks, spread across scopes.

    Grouped rather than laid flat because a scope adds a context and lengthens
    every task's mangled name, and mangled names are a large part of what is
    being measured (see docs/compile-scaling.md). Ten per scope matches the
    examples.
    """
    lines = ["system:"]
    for index in range(count):
        if index % per_scope == 0:
            lines.append(f"  sub_{index // per_scope:03d}:")
            lines.append("    type: scope")
            lines.append("    children:")
        lines.append(f"      task_{index:04d}:")
        lines.append("        type: polled_task")
        lines.append("        params: { level: float }")
        lines.append("        returns: { value: uint32 }")
    lines += ["links:", "  bench:", "    transport: uart"]
    return "\n".join(lines) + "\n"


def available_mb() -> int:
    """Free memory in MB, or -1 if it cannot be read."""
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    except OSError:
        pass
    return -1


def generate(work: Path, count: int, python: str) -> Optional[str]:
    """Scaffolds and generates a project of `count` tasks. Returns an error, or None."""
    work.mkdir(parents=True, exist_ok=True)
    (work / "schema.yaml").write_text(schema_for(count))
    steps = [
        [python, "-m", "etask.schema.cli", "scaffold", "--out", "."],
        [python, "-m", "etask.schema.cli", "generate", "schema.yaml",
         "--out", "sys",
         "--task-id", "generated/task_id.hpp",
         "--task-list", "generated/task_list.hpp",
         "--links", "generated/links.hpp",
         "--scopes", "generated/scopes.hpp"],
    ]
    for step in steps:
        done = subprocess.run(step, cwd=work, capture_output=True, text=True)
        if done.returncode != 0:
            return (done.stderr or done.stdout).strip().splitlines()[-1][:200]
    return None


def compile_probe(work: Path, compiler: str, cap_mb: int, extra: List[str]) -> Dict:
    """Compiles the probe once, serially, under an address-space cap.

    @return A dict with `ok`, `seconds`, `peak_rss_mb`, `object_bytes`, `error`.
    """
    probe = work / "probe.cpp"
    probe.write_text(PROBE)
    obj = work / "probe.o"

    # -ftemplate-depth mirrors what etools' CMake INTERFACE target hands a
    # consumer; this probe compiles by hand, so it has to pass it itself.
    argv = [compiler, "-std=c++17", "-Os", "-ftemplate-depth=8192",
            "-c", str(probe), "-o", str(obj),
            f"-I{work}", f"-I{REPO}",
            f"-I{ELIB}/etools", f"-I{ELIB}/ecomm", f"-I{ELIB}/eser",
            "-DECOMM_BOARD_ID=1", *extra]

    def cap() -> None:
        # The address-space cap is the whole safety story: a compile that would
        # have exhausted the machine dies here instead, as an ordinary failure.
        limit = cap_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))

    before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    start = time.monotonic()
    done = subprocess.run(argv, capture_output=True, text=True, preexec_fn=cap)
    seconds = time.monotonic() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss

    ok = done.returncode == 0
    error = ""
    if not ok:
        text = (done.stderr or done.stdout).strip()
        # A cap hit shows up as the compiler being unable to allocate.
        if "Cannot allocate memory" in text or "out of memory" in text.lower():
            error = f"exceeded the {cap_mb} MB address-space cap"
        elif done.returncode == -9:
            error = "killed (signal 9) - the OOM reaper, not the cap"
        else:
            error = text.splitlines()[-1][:200] if text else f"exit {done.returncode}"

    return {
        "ok": ok,
        "seconds": round(seconds, 2),
        # ru_maxrss is the high-water mark across all children, so the delta is
        # this compile's own peak only when it is the largest so far. It is, in a
        # monotonic ladder.
        "peak_rss_mb": round(max(after, before) / 1024, 1),
        "object_bytes": obj.stat().st_size if ok and obj.exists() else 0,
        "error": error,
    }


def uid_stats(work: Path) -> Dict:
    """Reads the ledger: uid width, and how densely the space is packed."""
    ledger = work / ".schema.uids.json"
    if not ledger.is_file():
        return {}
    try:
        data = json.loads(ledger.read_text())
    except (OSError, ValueError):
        return {}
    uids = list((data.get("uids") or {}).values())
    if not uids:
        return {}
    return {
        "uid_bytes": data.get("uid_bytes"),
        "max_uid": max(uids),
        "packed": max(uids) == len(uids) - 1,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--counts", type=int, nargs="+", default=DEFAULT_COUNTS,
                        help="task counts to measure")
    parser.add_argument("--compiler", default="g++", help="compiler to drive")
    parser.add_argument("--cflags", nargs="*", default=[],
                        help="extra compiler flags (e.g. -ggdb)")
    parser.add_argument("--cap-mb", type=int, default=3000,
                        help="address-space cap per compile; an over-run fails cleanly")
    parser.add_argument("--min-free-mb", type=int, default=3500,
                        help="stop the ladder if free memory drops below this")
    parser.add_argument("--log", type=Path, default=REPO / "bench" / "strain.jsonl",
                        help="results, one JSON object per line, appended as we go")
    parser.add_argument("--work", type=Path,
                        default=Path(os.environ.get("TMPDIR", "/tmp")) / "etask-strain",
                        help="where generated projects live")
    parser.add_argument("--python", default=str(REPO / "venv" / "bin" / "python"),
                        help="interpreter that has the etask package")
    parser.add_argument("--resume", action="store_true",
                        help="skip counts already present in the log")
    parser.add_argument("--keep", action="store_true",
                        help="keep generated projects (they are large)")
    args = parser.parse_args()

    if not shutil.which(args.compiler):
        print(f"no such compiler: {args.compiler}", file=sys.stderr)
        return 2

    done_counts = set()
    if args.resume and args.log.is_file():
        for line in args.log.read_text().splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("compiler") == args.compiler and row.get("ok"):
                done_counts.add(row.get("tasks"))

    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.work.mkdir(parents=True, exist_ok=True)

    print(f"# strain: {args.compiler}, cap {args.cap_mb} MB, "
          f"stop under {args.min_free_mb} MB free")
    print(f"# log: {args.log}")
    print(f"{'tasks':>6} {'time':>9} {'peak RSS':>10} {'object':>10} "
          f"{'uid B':>6} {'packed':>7}  note")

    for count in sorted(args.counts):
        if count in done_counts:
            print(f"{count:6d} {'(logged)':>9}")
            continue

        free = available_mb()
        if 0 <= free < args.min_free_mb:
            print(f"{count:6d} {'SKIPPED':>9}  only {free} MB free; stopping here")
            break

        work = args.work / str(count)
        error = generate(work, count, args.python)
        if error:
            print(f"{count:6d} {'GEN FAIL':>9}  {error}")
            break

        result = compile_probe(work, args.compiler, args.cap_mb, args.cflags)
        row = {
            "tasks": count,
            "compiler": args.compiler,
            "cflags": args.cflags,
            "free_mb_before": free,
            **result,
            **uid_stats(work),
        }
        # Appended per point: an interrupted ladder keeps what it measured.
        with args.log.open("a") as handle:
            handle.write(json.dumps(row) + "\n")

        if result["ok"]:
            print(f"{count:6d} {result['seconds']:8.1f}s "
                  f"{result['peak_rss_mb']:9.0f}M {result['object_bytes']:9d}B "
                  f"{row.get('uid_bytes', '?'):>6} {str(row.get('packed', '?')):>7}")
        else:
            print(f"{count:6d} {'FAILED':>9}  {result['error']}")

        if not args.keep:
            shutil.rmtree(work, ignore_errors=True)

        if not result["ok"]:
            # The ladder is monotonic: a larger schema cannot succeed where a
            # smaller one failed, so there is nothing above this worth trying.
            print(f"# stopped at {count} tasks")
            break

    return 0


if __name__ == "__main__":
    sys.exit(main())
