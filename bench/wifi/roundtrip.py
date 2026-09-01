#!/usr/bin/env python3
"""WiFi round-trip benchmark: PC -> board -> PC, over TCP.

Measures what it costs to command a task over WiFi and get its reply, and separates that into the
two things it is made of:

* **transport** - a bare echo task doing no work. This is the network plus the framing, and on
  WiFi it dominates everything by an order of magnitude.
* **framework** - the same round trip to a task that does real work, minus the echo. The
  difference is what etask contributes.

Reporting only the total would credit the network's latency to the framework (or hide the
framework inside it). The confounder here is the network, not the code, so the transport figure is
measured in the same run under the same conditions and printed alongside.

## What is reported, and why not just the mean

**Median and p95**, not the mean. WiFi latency is long-tailed - a single retransmit or a beacon
interval can be 100x the median - and a mean folds those into an average nobody experiences. For a
robotics control loop the tail is the number that decides whether a deadline is met, so p95 and
p99 are printed and the mean is shown only for reference.

## Two load regimes

* **sequential** - one request in flight, waiting for each reply. This is the honest latency.
* **pipelined**  - `--in-flight N` requests outstanding at once, which measures throughput and
  exposes whether the board's single-threaded `update()` loop becomes the bottleneck.

The board must be running bench/wifi/firmware. Usage::

    python3 bench/wifi/roundtrip.py --host 192.168.1.50            # sequential latency
    python3 bench/wifi/roundtrip.py --host 192.168.1.50 --in-flight 8
    python3 bench/wifi/roundtrip.py --host 192.168.1.50 --json data/wifi.json

Requires the local ecomm-python and etask-python on PYTHONPATH; see bench/README.md.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import sys
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path

try:
    from ecomm.channels.async_tcp_channel import AsyncTcpChannel
    from ecomm.protocol.schema import PacketSchema
    from ecomm.protocol.topology import Topology
    from ecomm.protocol.checksum import ChecksumPolicy
    from etask.client import Client
except ImportError as exc:  # pragma: no cover - an environment problem, not a benchmark result
    print(f"error: could not import the local siblings: {exc}", file=sys.stderr)
    print("       see bench/README.md for the PYTHONPATH the harness needs", file=sys.stderr)
    sys.exit(1)


# The uids the benchmark firmware registers. Must match bench/wifi/firmware/src/main.cpp.
UID_ECHO = 0x20          # oneshot, no work: pure transport
UID_LIGHT = 0x21         # oneshot, ~20 flops
UID_HEAVY = 0x22         # oneshot, ~500 flops
UID_INSTANT = 0x10       # instant command: NO REPLY (see below)

CASES = [
    ("echo (transport floor)", UID_ECHO),
    ("oneshot + light work", UID_LIGHT),
    ("oneshot + heavy work", UID_HEAVY),
]


@dataclass
class Stats:
    """Latency distribution for one case, in milliseconds."""
    label: str
    uid: int
    samples: int = 0
    lost: int = 0
    median_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    mean_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0
    raw_ms: list[float] = field(default_factory=list)

    @classmethod
    def of(cls, label: str, uid: int, timings: list[float], lost: int) -> "Stats":
        if not timings:
            return cls(label=label, uid=uid, lost=lost)
        ordered = sorted(timings)
        def pct(p: float) -> float:
            # Nearest-rank percentile: with a few hundred samples, interpolation implies a
            # precision the sample size does not support.
            idx = min(len(ordered) - 1, int(round(p * (len(ordered) - 1))))
            return ordered[idx]
        return cls(
            label=label, uid=uid, samples=len(timings), lost=lost,
            median_ms=statistics.median(ordered),
            p95_ms=pct(0.95), p99_ms=pct(0.99),
            mean_ms=statistics.fmean(ordered),
            min_ms=ordered[0], max_ms=ordered[-1],
            raw_ms=timings,
        )


async def measure_sequential(client: Client, uid: int, count: int, timeout: float
                             ) -> tuple[list[float], int]:
    """One request in flight at a time. This is the latency figure."""
    timings: list[float] = []
    lost = 0
    for _ in range(count):
        start = time.perf_counter()
        try:
            await asyncio.wait_for(client.launch(uid), timeout=timeout)
        except asyncio.TimeoutError:
            # A lost reply is a result, not a crash - WiFi drops packets. Counted and reported;
            # silently retrying would hide real packet loss behind a flattering latency figure.
            lost += 1
            continue
        timings.append((time.perf_counter() - start) * 1000.0)
    return timings, lost


async def measure_pipelined(client: Client, uid: int, count: int, in_flight: int, timeout: float
                            ) -> tuple[list[float], int]:
    """`in_flight` requests outstanding at once: throughput, and where the board saturates.

    Note the per-request timing here includes queueing behind the other outstanding requests, so
    these numbers are deliberately NOT comparable with the sequential ones. They answer a
    different question: how fast can the board be driven, not how fast is one command.
    """
    timings: list[float] = []
    lost = 0
    semaphore = asyncio.Semaphore(in_flight)

    async def one() -> None:
        nonlocal lost
        async with semaphore:
            start = time.perf_counter()
            try:
                await asyncio.wait_for(client.launch(uid), timeout=timeout)
            except asyncio.TimeoutError:
                lost += 1
                return
            timings.append((time.perf_counter() - start) * 1000.0)

    await asyncio.gather(*(one() for _ in range(count)))
    return timings, lost


def render(results: list[Stats], mode: str, in_flight: int) -> str:
    out: list[str] = []
    out.append("")
    header = f"== WiFi round trip, {mode}" + (f", {in_flight} in flight" if mode == "pipelined" else "")
    out.append(f"{header} ==")
    out.append("")
    out.append(f"  {'case':<26} {'median':>9} {'p95':>9} {'p99':>9} {'mean':>9} {'lost':>6}")
    out.append(f"  {'-'*26} {'-'*9} {'-'*9} {'-'*9} {'-'*9} {'-'*6}")
    for s in results:
        if not s.samples:
            out.append(f"  {s.label:<26} {'NO REPLY':>9}   ({s.lost} lost)")
            continue
        out.append(f"  {s.label:<26} {s.median_ms:>8.2f}m {s.p95_ms:>8.2f}m "
                   f"{s.p99_ms:>8.2f}m {s.mean_ms:>8.2f}m {s.lost:>6}")

    # The framework's own share, which is the whole point of measuring the echo case.
    echo = next((s for s in results if s.uid == UID_ECHO and s.samples), None)
    if echo:
        out.append("")
        out.append("  Framework share (case median - echo median):")
        for s in results:
            if s.uid == UID_ECHO or not s.samples:
                continue
            delta = s.median_ms - echo.median_ms
            out.append(f"    {s.label:<24} {delta:+8.2f} ms")
        out.append("")
        out.append(f"  The {echo.median_ms:.2f} ms echo floor is network + framing, not etask.")
        out.append("  On WiFi it dominates; the on-board task cost is in the runtime table, in ns.")
    return "\n".join(out)


async def run(args: argparse.Namespace) -> int:
    # Must match the firmware's packet_t exactly: 32 bytes, network topology (so replies can be
    # addressed back), no checksum (TCP already guarantees integrity).
    schema = PacketSchema(
        packet_size=32,
        topology=Topology.NETWORK,
        checksum=ChecksumPolicy.NONE,
    )

    print(f"connecting to {args.host}:{args.port} ...", flush=True)
    channel = await AsyncTcpChannel.connect(schema, args.host, args.port)

    results: list[Stats] = []
    try:
        async with Client(channel, uid_bytes=1, receiver_id=args.board_id) as client:
            # A few unmeasured requests first: the first packet pays for ARP, the TCP window
            # opening, and any lazy allocation on the board. Including it would put a one-off cost
            # into the distribution as a fake tail.
            print(f"warming up ({args.warmup} requests) ...", flush=True)
            await measure_sequential(client, UID_ECHO, args.warmup, args.timeout)

            for label, uid in CASES:
                print(f"measuring {label} ({args.count} requests) ...", flush=True)
                if args.in_flight > 1:
                    timings, lost = await measure_pipelined(
                        client, uid, args.count, args.in_flight, args.timeout)
                else:
                    timings, lost = await measure_sequential(
                        client, uid, args.count, args.timeout)
                results.append(Stats.of(label, uid, timings, lost))
    finally:
        await channel.close()

    mode = "pipelined" if args.in_flight > 1 else "sequential"
    print(render(results, mode, args.in_flight))

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(
            {"mode": mode, "in_flight": args.in_flight, "host": args.host,
             "cases": [asdict(s) for s in results]}, indent=2))
        print(f"\nraw records -> {args.json}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="etask WiFi round-trip benchmark")
    ap.add_argument("--host", required=True, help="board's IP address")
    ap.add_argument("--port", type=int, default=3333, help="board's TCP port (default 3333)")
    ap.add_argument("--board-id", type=int, default=1, help="the board's ecomm node id")
    ap.add_argument("--count", type=int, default=200, help="requests per case (default 200)")
    ap.add_argument("--warmup", type=int, default=20, help="unmeasured requests first (default 20)")
    ap.add_argument("--in-flight", type=int, default=1,
                    help="outstanding requests; >1 measures throughput, not latency")
    ap.add_argument("--timeout", type=float, default=2.0, help="per-request timeout, seconds")
    ap.add_argument("--json", type=Path, help="write raw records here")
    args = ap.parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    sys.exit(main())
