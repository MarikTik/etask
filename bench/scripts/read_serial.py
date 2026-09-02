#!/usr/bin/env python3
"""Capture a benchmark run from the board's serial port, logging as it arrives.

`pio device monitor` needs a TTY and crashes in a non-interactive shell, so the
runtime tracks are read with pyserial instead. This script does that, and adds
the two things the benchmarking conventions ask for:

**It writes each line to the log as it arrives**, never at the end. A run that
is interrupted - board reset, cable knocked, session killed - keeps everything
it had already printed. Results held only in a terminal scrollback are lost the
moment anything goes wrong.

**It fails loudly when the port is absent.** A runtime harness that silently
reports nothing when no board is attached is worse than one that stops, because
an empty table reads like a measured zero.

Usage:
    bench/scripts/read_serial.py --out bench/data/runtime-esp32dev.txt
    bench/scripts/read_serial.py --until '=== done ===' --timeout 300
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

try:
    import serial
except ImportError:
    sys.exit("pyserial is not installed: pip install pyserial")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--port", default="/dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--out", type=Path, help="append each line here as it arrives")
    parser.add_argument("--until", default="=== done ===",
                        help="stop once this appears in a line")
    parser.add_argument("--timeout", type=float, default=300.0,
                        help="give up after this many seconds")
    parser.add_argument("--no-reset", action="store_true",
                        help="do not toggle DTR/RTS (keeps a running sketch running)")
    args = parser.parse_args()

    # Fail loudly rather than reporting an empty run: an absent board must not
    # look like a measurement of nothing.
    if not Path(args.port).exists():
        sys.exit(f"no board at {args.port} - attach one, or pass --port. "
                 f"Refusing to report an empty run.")

    handle = None
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        handle = args.out.open("a")
        handle.write(f"\n# --- run started {time.strftime('%Y-%m-%d %H:%M:%S')} "
                     f"port={args.port} baud={args.baud} ---\n")
        handle.flush()

    try:
        port = serial.Serial(args.port, args.baud, timeout=1)
    except serial.SerialException as exc:
        sys.exit(f"cannot open {args.port}: {exc}")

    if not args.no_reset:
        # Toggle DTR/RTS to reset the board, so setup() re-runs and its output
        # is captured from the first line rather than joined mid-table.
        port.dtr = False
        port.rts = False
        time.sleep(0.1)
        port.dtr = True
        port.rts = True

    deadline = time.time() + args.timeout
    saw_anything = False
    try:
        while time.time() < deadline:
            raw = port.readline()
            if not raw:
                continue
            line = raw.decode(errors="replace").rstrip("\r\n")
            saw_anything = True
            print(line, flush=True)
            if handle:
                # Flushed per line: an interrupted run keeps what it printed.
                handle.write(line + "\n")
                handle.flush()
            if args.until and args.until in line:
                break
        else:
            print(f"# timed out after {args.timeout:.0f}s without seeing "
                  f"{args.until!r}", file=sys.stderr)
    finally:
        port.close()
        if handle:
            handle.close()

    if not saw_anything:
        sys.exit(f"no output from {args.port} in {args.timeout:.0f}s - the board may "
                 f"not be running the benchmark firmware. Refusing to report an "
                 f"empty run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
