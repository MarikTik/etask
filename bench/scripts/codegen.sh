#!/usr/bin/env bash
#
# Codegen-quality check: count instructions for etask's dispatch and tick paths against the
# hand-written equivalents.
#
# This is the claim a size table cannot settle. Size deltas say the framework costs bytes; only
# disassembly says whether a *dispatch* costs more instructions than the `if` block it replaces,
# and whether that cost grows with the task count.
#
# Four comparisons, each a `extern "C"` function so it survives to the object file intact:
#
#   1. instant dispatch, 4 tasks   vs a hand-written switch
#   2. instant dispatch, 16 tasks  vs the same switch at 16 arms
#      -> the pair says whether etask's uid routing is O(1) or O(n) in code size. instant_task_
#         manager routes with a linear fold of `if`s, NOT a perfect hash, so a rising figure here
#         is expected and is the honest result to publish.
#   3. polled update() tick        vs a hand-written loop over a function-pointer table
#      -> the virtual-call question: two virtual calls (on_execute, is_finished) plus the
#         manager's bookkeeping, against one indirect call.
#   4. dispatch_factory::emplace   vs a switch constructing in place
#      -> the perfect-hash claim for the managed tiers, which DO use dispatch_factory.
#
# Usage: bench/scripts/codegen.sh [target]
#   target: host (default) | xtensa | xtensa32 | arm
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"   # etask/
ELIB="$(cd "$ROOT/.." && pwd)"                               # elib/
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

TARGET="${1:-host}"

case "$TARGET" in
  host)     CXX="g++"; FLAGS="-O2 -std=c++17" ;;
  # The ESP8266 core's compiler (GCC 10.3).
  xtensa)   CXX="$HOME/.platformio/packages/toolchain-xtensa/bin/xtensa-lx106-elf-g++"
            FLAGS="-O2 -std=c++17" ;;
  # The ESP32 core's compiler (GCC 8.4) - the one that could not parse an attribute on a
  # constructor's first parameter. Worth checking separately: a different compiler generation can
  # optimize the fold differently.
  xtensa32) CXX="$HOME/.platformio/packages/toolchain-xtensa-esp32/bin/xtensa-esp32-elf-g++"
            FLAGS="-O2 -std=c++17" ;;
  arm)      CXX="$(find "$HOME/.platformio/packages" -name 'arm-none-eabi-g++' | head -1)"
            FLAGS="-O2 -std=c++17 -mcpu=cortex-m4 -mthumb --specs=nosys.specs" ;;
  *)        echo "unknown target: $TARGET (expected host|xtensa|xtensa32|arm)" >&2; exit 2 ;;
esac

if [ -z "${CXX:-}" ] || ! command -v "$CXX" >/dev/null 2>&1; then
  echo "codegen: toolchain for '$TARGET' not found; skipping" >&2
  exit 0
fi

cp "$ROOT/bench/codegen/cg.cpp" "$WORK/cg.cpp"

"$CXX" $FLAGS \
  -I"$ELIB/etask" -I"$ELIB/etools" -I"$ELIB/ecomm" -I"$ELIB/eser" \
  -c "$WORK/cg.cpp" -o "$WORK/cg.o"

OBJDUMP="${CXX%g++}objdump"
command -v "$OBJDUMP" >/dev/null 2>&1 || OBJDUMP="objdump"

dump_fn() {
  "$OBJDUMP" -d --no-show-raw-insn "$WORK/cg.o" \
    | awk -v fn="$1" '
        $0 ~ "<"fn">:" {inside=1; next}
        inside && /^$/  {inside=0}
        inside          {sub(/^[[:space:]]*[0-9a-f]+:[[:space:]]*/, ""); print}
      '
}

count_fn() { dump_fn "$1" | grep -c . || true; }

echo "=== etask codegen quality ($TARGET, $FLAGS) ==="
echo

printf '%s\n' "-- 1/2. instant dispatch: etask vs a hand-written switch --"
for n in 4 16; do
  HAND=$(count_fn "hand_dispatch_$n")
  ETASK=$(count_fn "etask_dispatch_$n")
  printf '  %-34s hand %4s   etask %4s   delta %+d\n' \
    "$n tasks" "$HAND" "$ETASK" "$((ETASK - HAND))"
done
echo
echo "  instant_task_manager routes with a linear fold of if-comparisons, not a perfect hash, so"
echo "  its code grows with the task count. So does the switch it is compared against, and the"
echo "  delta is what matters: a NEGATIVE delta means the fold compiled tighter than the"
echo "  compiler's own switch lowering (it can pick a jump table the fold does not need)."
echo "  Read the two rows together - a delta that WORSENS from 4 to 16 is the fold losing to the"
echo "  switch as the chain lengthens; one that stays flat or improves is not."
echo

printf '%s\n' "-- 3. polled update() tick vs a hand-written function-pointer loop --"
HAND_TICK=$(count_fn hand_tick)
ETASK_TICK=$(count_fn etask_tick)
printf '  %-34s hand %4s   etask %4s   delta %+d\n' \
  "1 live task" "$HAND_TICK" "$ETASK_TICK" "$((ETASK_TICK - HAND_TICK))"
echo
echo "  etask makes two virtual calls per tick (on_execute, is_finished) plus its bookkeeping;"
echo "  the reference makes one indirect call. Note etask_tick is NOT inlined into a loop here,"
echo "  so this counts the tick body, not a whole loop - read it with the runtime table."
echo

printf '%s\n' "-- 4. dispatch_factory::emplace vs a switch constructing in place --"
HAND_EM=$(count_fn hand_emplace)
ETASK_EM=$(count_fn etask_emplace)
printf '  %-34s hand %4s   etask %4s   delta %+d\n' \
  "8 registered types" "$HAND_EM" "$ETASK_EM" "$((ETASK_EM - HAND_EM))"
echo
echo "  The managed tiers DO use dispatch_factory (etools perfect hash), so this is the one that"
echo "  should be close to constant. Compare against comparison 1, which does not."
echo

echo "--- etask_dispatch_4 ---"
dump_fn etask_dispatch_4
echo
echo "--- etask_tick ---"
dump_fn etask_tick
