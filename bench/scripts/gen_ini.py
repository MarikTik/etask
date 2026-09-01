#!/usr/bin/env python3
"""Generate bench/platformio.ini: the cross product of boards, feature tiers, build modes, and
the task-count ladder.

Hand-maintaining that many env blocks invites copy-paste drift, and a benchmark whose environments
quietly disagree measures nothing. Regenerate instead::

    python3 bench/scripts/gen_ini.py > bench/platformio.ini

Two ladders are emitted:

* ``<board>_<mode>_t<n>``  - the feature ladder. Consecutive tiers differ by one feature.
* ``<board>_<mode>_n<k>``  - the task-count ladder, all at tier 5 (full framework), varying only
  how many tasks are registered. The slope is the marginal flash cost per task, which answers
  "how does this scale" - the question the eser suite had no equivalent for.

Build modes matter as much as tiers: etask's contracts are ``assert``, which exists only while
``NDEBUG`` is undefined. A release-only table would report every contract check as free.
"""

from __future__ import annotations

import sys

# The working tree of elib, so etask/etools/ecomm/eser all resolve locally rather than from the
# PlatformIO registry. ecomm in particular is under active local development and its tree differs
# from the published 3.0.1 - a registry build would measure different code. RESULTS.md must state
# which commit of each sibling was measured.
ELIB_ROOT = "/home/mark/Desktop/projects/elib"

# (board id, platformio board, platform, comment)
BOARDS = [
    ("esp32dev", "esp32dev", "espressif32",
     "ESP32-D0WD (LX6), GCC 8.4. Plain ESP32 devkit, WROOM-32 and WROOM-32U all map here:\n"
     "; same die and core; WROOM-32U differs only by U.FL external antenna."),
    ("esp32s3", "esp32-s3-devkitc-1", "espressif32",
     "ESP32-S3-WROOM-1 (LX7), GCC 8.4. Distinct core from the LX6 above."),
    ("nodemcuv2", "nodemcuv2", "espressif8266",
     "ESP8266 NodeMCU, GCC 10.3 and 80 MHz. PlatformIO has no separate v3 id; v3 boards use\n"
     "; this same ESP-12E target."),
    ("stm32f411", "blackpill_f411ce", "ststm32",
     "STM32F411 (Cortex-M4). Compile-only portability check: no such board is on hand, so its\n"
     "; footprint is measured but its runtime cost is not."),
]

# (mode id, build_type, extra flags, extra unflags)
#
# The debug mode must unflag -DNDEBUG: some platforms (STM32duino among them) inject it into their
# own default build_flags even for build_type = debug, which silently compiles out every assert and
# makes the debug column measure the same thing as release.
MODES = [
    ("rel", "release", "-Os -DNDEBUG", ""),
    ("relO2", "release", "-O2 -DNDEBUG", ""),
    ("dbg", "debug", "-Og", "-DNDEBUG"),
    # Same as `rel` but with RTTI off. Paired with it deliberately: the delta
    # between the two columns is what typeinfo costs, and it is only meaningful
    # if nothing else differs.
    #
    # Worth a mode of its own because the answer is large and nothing else in
    # this suite reveals it. etask, ecomm, etools and eser contain no
    # `dynamic_cast` and no `typeid` - verified by grep across all four - but
    # they do use virtual dispatch, so the compiler emits a vtable, a typeinfo
    # object and a typeinfo *name string* for every task, and again for the
    # unpacking adapter it generates per task. Nothing ever reads any of it.
    #
    # It only shows up from tier 7, where a task is registered from a
    # `buffer_view` and the adapters are therefore instantiated. Below that tier
    # the two columns should agree closely, and if they do not, something else
    # changed between them.
    ("relNoRtti", "release", "-Os -DNDEBUG -fno-rtti", ""),
]

TIERS = range(0, 8)

# Task counts for the scaling ladder, all at tier 5.
TASK_COUNTS = [1, 2, 4, 8, 16, 32]

TIER_COMMENT = """; Feature ladder (see bench/src/main.cpp):
;   0  framework + sink only, etask not included    -> the floor
;   1  + #include <etask/core/core.hpp>, nothing used -> header-only cost (must be 0 B)
;   2  + task_manager with 1 instant command
;   3  + a 2nd instant command                      -> marginal cost of one instant task
;   4  + the polled tier                            -> vector, bitset, dispatch_factory, vtables
;   5  + the stateful tier                          -> full framework, all three managers
;   6  + internal channel
;   7  + external channel                           -> pulls in ecomm packet + eser codec
;
; Task-count ladder (all at tier 5, varying BENCH_TASKS): 1, 2, 4, 8, 16, 32 registered tasks.
; The slope is the marginal flash cost per registered task.
;
; Build modes:
;   rel    -Os -DNDEBUG   size-optimized release; asserts compiled out (what ships)
;   relO2  -O2 -DNDEBUG   speed-optimized release; asserts compiled out
;   dbg    -Og            debug; etask's assert contracts are LIVE and cost real bytes
;   relNoRtti  -Os -DNDEBUG -fno-rtti   as rel, minus typeinfo. rel minus this is
;                                       what RTTI costs; visible from tier 7 up"""


def main() -> int:
    out: list[str] = []
    out.append("; etask static-footprint benchmark -- GENERATED FILE, DO NOT EDIT BY HAND.")
    out.append("; Regenerate with: python3 bench/scripts/gen_ini.py > bench/platformio.ini")
    out.append(";")
    out.append("; Each env builds bench/src/main.cpp at one point of the ladder and one build mode.")
    out.append("; Subtracting consecutive points within a mode gives the incremental cost.")
    out.append(";")
    out.append(TIER_COMMENT)
    out.append("")
    out.append("[platformio]")
    out.append("src_dir = src")
    out.append("")
    out.append("[env]")
    out.append("framework = arduino")
    # Only the language standard is unflagged. Listing -Os/-O2/-Og here would strip the
    # optimization level this benchmark is trying to set: build_unflags is applied AFTER
    # build_flags, so the mode's own -O would be removed and every point would silently compile at
    # -O0, inflating measured cost by roughly an order of magnitude. On ESP8266 this once reported
    # 13600 B where the truth was 888 B.
    out.append("build_unflags = -std=gnu++11 -std=gnu++14")
    # Resolve the siblings from the working tree, not the registry.
    out.append(f"lib_extra_dirs = {ELIB_ROOT}")
    out.append("lib_ldf_mode = deep+")
    out.append("lib_deps =")
    out.append("")

    for board_id, pio_board, platform, comment in BOARDS:
        out.append(f"; {'-' * 74}")
        for line in comment.split("\n"):
            out.append(f"; {line}" if not line.startswith(";") else line)
        out.append(f"[{board_id}_base]")
        out.append(f"platform = {platform}")
        out.append(f"board = {pio_board}")
        out.append("")

        for mode_id, build_type, mode_flags, mode_unflags in MODES:
            def emit(env_name: str, defines: str) -> None:
                out.append(f"[env:{env_name}]")
                out.append(f"extends = {board_id}_base")
                out.append(f"build_type = {build_type}")
                out.append(f"build_flags = -std=gnu++17 {mode_flags} {defines}")
                if mode_unflags:
                    out.append(f"build_unflags = -std=gnu++11 -std=gnu++14 {mode_unflags}")
                out.append("")

            for tier in TIERS:
                emit(f"{board_id}_{mode_id}_t{tier}", f"-D BENCH_TIER={tier}")

            # The scaling ladder. Tier 5 is the full framework, so the only thing varying is the
            # number of registered tasks.
            for count in TASK_COUNTS:
                emit(f"{board_id}_{mode_id}_n{count}",
                     f"-D BENCH_TIER=5 -D BENCH_TASKS={count}")

            # The same ladder at tier 7, where a task is registered from a
            # `buffer_view` and so its unpacking adapter is instantiated.
            #
            # A second ladder rather than moving the first, because the two
            # answer different questions and both are wanted: tier 5 is the
            # marginal cost of a task the application starts itself, tier 7 the
            # marginal cost of one reachable over the wire. Only the latter pays
            # for an adapter - a second vtable, a second typeinfo object and a
            # second typeinfo name string per task - so only the latter shows
            # what `-fno-rtti` is worth. The tier-5 ladder measured against
            # `relNoRtti` reports almost nothing, which is true and misleading.
            for count in TASK_COUNTS:
                emit(f"{board_id}_{mode_id}_w{count}",
                     f"-D BENCH_TIER=7 -D BENCH_TASKS={count}")

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
