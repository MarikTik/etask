#!/usr/bin/env python3
"""Measures what RTTI costs an etask project, across a range of task counts.

Produces the table in `docs/flash-budget.md`. The question it answers is one a
user has at design time and cannot otherwise answer without building: "will a
tree this size fit, and what does turning RTTI off buy me?"

Every number here is measured, never extrapolated - the whole point of the
exercise was discovering that per-task cost *climbs* with tree size, so a figure
derived from a small prototype is wrong in the unsafe direction.

Usage:
    scripts/measure_rtti.py                  # host, the default ladder
    scripts/measure_rtti.py --counts 50 100  # a specific ladder
    scripts/measure_rtti.py --keep           # leave the builds for inspection
    scripts/measure_rtti.py --jobs 4         # allow four compilers at once

**This build is deliberately throttled.** Every task is its own translation unit
including heavily-templated headers, and each compiler process can want one or
two gigabytes. `-j$(nproc)` on an eight-core workstation is enough to invoke the
OOM killer and take the user's editor with it - measured, not hypothetical.
Measuring is never urgent enough to be worth that, so `--jobs` defaults to 2 and
going higher warns.

Every size this reports is in **bytes**, from `size -A` on the linked binary.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional


#: Where the repository is, from this file. The generator and the headers both
#: come from the checkout being measured, not from an installed copy.
REPO = Path(__file__).resolve().parent.parent

#: Task counts to measure. Chosen to bracket the sizes real projects reach and
#: to cross the uid-width boundary at 256, where the wire format changes.
#:
#: Kept short deliberately: each entry is two full builds, and the largest are
#: minutes of serial compilation. A ladder long enough to be pretty is a ladder
#: nobody runs.
DEFAULT_COUNTS = [25, 50, 100, 200, 300]

#: The sections that end up in flash on a microcontroller. `.text` is code;
#: `.rodata` holds typeinfo *names*; `.data.rel.ro` holds vtables and typeinfo
#: objects. Keeping them apart is what makes the RTTI story legible - RTTI moves
#: the latter two and leaves `.text` alone.
FLASH_SECTIONS = (".text", ".rodata", ".data.rel.ro")


def schema_for(count: int) -> str:
    """Builds a schema with `count` tasks, shaped like a real project.

    Tasks are spread across scopes rather than laid flat, because a scope adds a
    context and lengthens every task's mangled name - and the mangled names are
    what is being measured. Ten per scope is typical of the examples.

    @param count How many tasks the schema should declare.
    @return The schema as YAML text.
    """
    lines = ["system:"]
    per_scope = 10

    for index in range(count):
        scope = index // per_scope
        if index % per_scope == 0:
            lines.append(f"  subsystem_{scope:02d}:")
            lines.append("    type: scope")
            lines.append("    children:")
        # A parameter and a return, so the task carries a real wire contract:
        # an argument-less task would skip the unpack adapter entirely and
        # measure something other than what a project actually pays for.
        lines.append(f"      task_{index:03d}:")
        lines.append("        type: polled_task")
        lines.append("        params: { level: float }")
        lines.append("        returns: { value: uint32 }")

    # A link, so `main.cpp` can build an external_channel - which is what causes
    # the unpacking adapters to be instantiated at all. See `main_cpp`.
    lines.append("links:")
    lines.append("  bench:")
    lines.append("    transport: uart")

    return "\n".join(lines) + "\n"


def main_cpp() -> str:
    """The translation unit that instantiates the manager.

    Nothing here is measured for its own size; it exists so the manager, the
    factory and every task's adapter are actually instantiated. A manager that
    is merely declared emits none of the metadata under study.
    """
    return """\
#include "generated/task_list.hpp"
#include "generated/links.hpp"
#include <etask/core/managers/task_manager.hpp>
#include <etask/core/channels/external_channel.hpp>
#include <etask/core/channels/internal_channel.hpp>
#include <etools/memory/buffer_view.hpp>
#include <cstddef>
#include <optional>

using manager_t = etask::core::managers::task_manager_from_t<
    generated::instant_tasks,
    generated::polled_tasks,
    generated::stateful_tasks,
    generated::polled_budget,
    generated::stateful_budget>;

namespace links = generated::links;

// A hub that does nothing, so the channel instantiates without a transport.
struct null_hub {
    template<typename P> std::optional<P> try_receive() { return std::nullopt; }
    bool send(const links::bench::reply_packet_t&) { return true; }
};

namespace {
    manager_t manager{};
    null_hub hub{};
    etask::core::channels::internal_channel<manager_t> internal{manager};

    // The external channel is what makes this measurement honest. A task's
    // unpacking adapter - and so the adapter's typeinfo, which is most of what
    // is being measured - is only instantiated on the path that builds a task
    // from a payload. A manager alone emits none of it, and a harness without
    // this line reports identical numbers no matter what the adapter's type is
    // called.
    etask::core::channels::external_channel<links::bench::traits, null_hub, manager_t>
        external{hub, manager};
}

int main()
{
    manager.update();
    external.update();

    // Registered with a `buffer_view`, not with typed arguments. That is the
    // whole point: the payload overload is what selects a task's *unpacking
    // adapter*, and the adapter is where the scope binding lives and where most
    // of the RTTI is emitted. Calling `register_task(uid)` with no payload
    // instantiates the bare task instead, and the measurement then reports
    // identical numbers no matter what the adapter's type is called - which is
    // exactly the mistake an earlier version of this script made.
    // Every uid, not one. A uid is a runtime value, so the registry dispatches
    // on it through a table that names *every* task's adapter - but the linker
    // only emits an adapter's vtable and typeinfo if something actually reaches
    // that entry. Registering a single uid leaves the rest as inlined
    // constructors with no polymorphic footprint at all, and the measurement
    // then misses exactly the symbols under study.
    int accepted = 0;
    std::byte payload[8]{};
    for (unsigned uid = 0; uid <= 0xFFFF; ++uid) {
        const auto code = internal.register_task(
            static_cast<manager_t::task_uid_t>(uid),
            etools::memory::buffer_view{payload, sizeof(payload)});
        if (code == etask::core::status_code::ok)
            ++accepted;
        manager.update();
    }
    return accepted == 0;
}
"""


def cmakelists(rtti: bool) -> str:
    """The project's CMakeLists, with RTTI on or off.

    @param rtti Whether to compile with RTTI. `False` adds `-fno-rtti`.
    @return The CMake text.
    """
    flags = "" if rtti else "\ntarget_compile_options(probe PRIVATE -fno-rtti)"
    return f"""\
cmake_minimum_required(VERSION 3.20)
project(rtti_probe LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_subdirectory({REPO} etask_build)

file(GLOB_RECURSE TASK_SOURCES CONFIGURE_DEPENDS "${{CMAKE_CURRENT_SOURCE_DIR}}/sys/*.cpp")
add_executable(probe main.cpp ${{TASK_SOURCES}})
target_include_directories(probe PRIVATE ${{CMAKE_CURRENT_SOURCE_DIR}})
target_link_libraries(probe PRIVATE etask){flags}
"""


def build(count: int, rtti: bool, workspace: Path, jobs: int = 1) -> Optional[Dict[str, int]]:
    """Generates, builds and measures one project.

    @param count How many tasks.
    @param rtti Whether to compile with RTTI.
    @param workspace Directory to build in; created.
    @param jobs Parallel compile jobs. One by default - see the module docstring;
           each job can want a gigabyte or more, and this runs on a workstation
           someone is using at the time.
    @return Section sizes in bytes, or `None` if the build failed.
    """
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "schema.yaml").write_text(schema_for(count))
    (workspace / "main.cpp").write_text(main_cpp())
    (workspace / "CMakeLists.txt").write_text(cmakelists(rtti))

    generated = workspace / "generated"
    generated.mkdir(exist_ok=True)

    generate = subprocess.run(
        [sys.executable, "-m", "etask.schema.cli", "generate", "schema.yaml",
         "--out", "sys",
         "--task-id", "generated/task_id.hpp",
         "--task-list", "generated/task_list.hpp",
         "--scopes", "generated/scopes.hpp",
         "--links", "generated/links.hpp"],
        cwd=workspace, capture_output=True, text=True,
        env={**_env(), "PYTHONPATH": str(REPO / "etask-python")},
    )
    if generate.returncode != 0:
        print(f"  generate failed: {generate.stderr.strip()[:200]}", file=sys.stderr)
        return None

    configure = subprocess.run(
        ["cmake", "-S", ".", "-B", "build", "-DCMAKE_BUILD_TYPE=Release",
         "-DETASK_BUILD_TESTS=OFF", "-DETASK_BUILD_EXAMPLES=OFF"],
        cwd=workspace, capture_output=True, text=True,
    )
    if configure.returncode != 0:
        print(f"  configure failed: {configure.stderr.strip()[:300]}", file=sys.stderr)
        return None

    compile_result = subprocess.run(
        ["cmake", "--build", "build", "-j", str(jobs)],
        cwd=workspace, capture_output=True, text=True,
    )
    if compile_result.returncode != 0:
        print(f"  build failed: {compile_result.stderr.strip()[:300]}", file=sys.stderr)
        return None

    return sections(workspace / "build" / "probe")


def sections(binary: Path) -> Dict[str, int]:
    """Reads the flash-relevant section sizes out of a built binary.

    @param binary The executable to measure.
    @return Section name to size in bytes, plus a `total` of the three.
    """
    output = subprocess.run(
        ["size", "-A", str(binary)], capture_output=True, text=True, check=True
    ).stdout

    found = {name: 0 for name in FLASH_SECTIONS}
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] in found:
            found[parts[0]] = int(parts[1])

    found["total"] = sum(found[name] for name in FLASH_SECTIONS)
    return found


def _env() -> Dict[str, str]:
    """The environment for a subprocess, without inheriting a stale PYTHONPATH."""
    import os
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    return env


def render(rows: List[Dict]) -> str:
    """Renders the measurements as the markdown table users read.

    @param rows One entry per task count, each holding both measurements.
    @return The table, with a per-task column - which is the figure that shows
            the cost is not linear.
    """
    out = [
        "Flash footprint (.text + .rodata + .data.rel.ro), in BYTES.",
        "",
        "| tasks | with RTTI (bytes) | with -fno-rtti (bytes) | saved (bytes) | saved (%) "
        "| with RTTI, bytes/task | with -fno-rtti, bytes/task |",
        "|------:|------------------:|-----------------------:|--------------:|---------:"
        "|----------------------:|---------------------------:|",
    ]
    for row in rows:
        with_rtti = row["rtti"]["total"]
        without = row["nortti"]["total"]
        saved = with_rtti - without
        out.append(
            f"| {row['count']} | {with_rtti:,} | {without:,} | {saved:,} | "
            f"{saved * 100 // with_rtti}% | {with_rtti // row['count']:,} | "
            f"{without // row['count']:,} |"
        )
    return "\n".join(out)


def render_sections(rows: List[Dict]) -> str:
    """Renders the per-section breakdown, which is where the story is.

    @param rows One entry per task count.
    @return A table showing that `.text` does not move and the metadata does.
    """
    out = [
        "Per-section sizes, in BYTES. Every column is one ELF section as reported",
        "by `size -A`. '.text' is executable code; '.rodata' holds typeinfo NAME",
        "strings; '.data.rel.ro' holds vtables and typeinfo objects.",
        "",
        "| tasks | .text with RTTI (bytes) | .text with -fno-rtti (bytes) "
        "| .rodata with RTTI (bytes) | .rodata with -fno-rtti (bytes) "
        "| .data.rel.ro with RTTI (bytes) | .data.rel.ro with -fno-rtti (bytes) |",
        "|------:|------------------------:|-----------------------------:"
        "|--------------------------:|------------------------------:"
        "|-------------------------------:|------------------------------------:|",
    ]
    for row in rows:
        rtti, off = row["rtti"], row["nortti"]
        out.append(
            f"| {row['count']} | {rtti['.text']:,} | {off['.text']:,} "
            f"| {rtti['.rodata']:,} | {off['.rodata']:,} "
            f"| {rtti['.data.rel.ro']:,} | {off['.data.rel.ro']:,} |"
        )
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--counts", type=int, nargs="+", default=DEFAULT_COUNTS)
    parser.add_argument("--keep", action="store_true",
                        help="leave the generated projects in place for inspection")
    parser.add_argument("--json", type=Path, help="also write the raw measurements here")
    parser.add_argument("--jobs", type=int, default=2,
                        help="parallel compile jobs (default 2; each can want >1GB)")
    args = parser.parse_args()

    if args.jobs > 2:
        print(f"warning: building with -j{args.jobs}; each job can want more than "
              "a gigabyte, and this machine is presumably in use.", file=sys.stderr)

    root = Path(tempfile.mkdtemp(prefix="etask-rtti-"))
    rows: List[Dict] = []

    try:
        for count in args.counts:
            print(f"measuring {count} tasks...", flush=True)
            row: Dict = {"count": count}

            for label, rtti in (("rtti", True), ("nortti", False)):
                result = build(count, rtti, root / f"{count}-{label}", args.jobs)
                if result is None:
                    print(f"  {label}: FAILED", file=sys.stderr)
                    break
                row[label] = result
                print(f"  {label}: total {result['total']:,}")
            else:
                rows.append(row)

        if not rows:
            print("no measurements completed", file=sys.stderr)
            return 1

        print("\n## Totals\n")
        print(render(rows))
        print("\n## By section\n")
        print(render_sections(rows))

        if args.json:
            args.json.write_text(json.dumps(rows, indent=2))
            print(f"\nraw measurements -> {args.json}")
    finally:
        if args.keep:
            print(f"\nbuilds left in {root}")
        else:
            shutil.rmtree(root, ignore_errors=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
