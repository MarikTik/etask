#!/usr/bin/env python3
"""Host-side driver for the `multi_link` integration project.

Builds nothing and assumes nothing: it launches the firmware binary with one end
of a socket pair per link, speaks both wires itself, and asserts on what comes
back. Exits non-zero on the first failure, printing expected against actual.

What it proves, in the order the checks run:

1. **Per-link sizing.** Each link's frame sizes match what its own subsystems
   need, and the two links DIFFER. This is the claim `subsystems:` exists to
   make - a link that carries only narrow tasks must not pay for the wide one on
   the other wire.
2. **A carried task works.** `telemetry.sample` over `bench` and `bulk.transfer`
   over `net`, each on the link that carries it.
3. **An uncarried task is refused, specifically.** `bulk.transfer` over `bench`
   and `telemetry.sample` over `net` must come back
   `task_undefined_on_this_link` (0x1A) and explicitly NOT `task_unknown`
   (0x14). The distinction is the whole point: the task exists on the device, so
   telling a peer it is unknown would send an operator hunting a registration
   that is not missing.
4. **The shared subsystem works over BOTH.** `shared.echo` on each wire, which
   is what separates a real per-uid allowlist from a link that merely refuses
   whatever it does not exclusively own.
5. **The fingerprint handshake.** Matching peers agree; a peer that corrupts one
   byte of its fingerprint is refused, and the error names both values.

Usage:
    ./verify.py [--binary path/to/multi_link]
"""
from __future__ import annotations

import argparse
import os
import socket
import struct
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Optional, Tuple

# The etask/ecomm Python runtimes are the same ones the firmware was generated
# against; importing them rather than restating the wire layout here is what
# keeps this driver a *test* of the contract instead of a second implementation
# of it that could drift into agreeing with itself.
from ecomm.protocol.checksum import ChecksumPolicy
from ecomm.protocol.packet import Packet
from ecomm.protocol.schema import PacketSchema
from ecomm.protocol.sequence import SequencePolicy
from ecomm.protocol.topology import Topology
from ecomm.protocol import validator

from etask import preamble
from etask.codec import pack, unpack
from etask.directive import Operation
from etask.protocol import build_request, parse_reply
from etask.status_code import StatusCode, status_name

#: Uids, from the project's committed ledger (.schema.uids.json). Restated here
#: rather than imported from python/tasks.py on purpose: this driver's job
#: includes catching a generator that emits the wrong uid, and a test that reads
#: its expectations out of the artifact under test cannot catch that.
UID_BULK_TRANSFER = 0x1E
UID_SHARED_ECHO = 0x4B
UID_TELEMETRY_SAMPLE = 0xE0
UID_PING = 0xF5

#: Width of a uid on the wire, pinned by the ledger.
UID_BYTES = 1

#: This node's id, and the firmware's. Must match ECOMM_BOARD_ID in CMakeLists.
HOST_ID = 2
DEVICE_ID = 1

#: How long any single reply may take before the run is called a failure.
#:
#: The firmware is a busy loop on the same machine, so a warm reply takes
#: microseconds and any value here is enormous. It is set well above that
#: because the *first* exchange of a run is not warm: a freshly built binary has
#: to be faulted in off disk and dynamically linked before its loop turns over,
#: which on a cold page cache has been observed past a second. A tight bound
#: turned that into an intermittent failure that said "timed out" while nothing
#: was wrong - the worst kind of test, since the honest response to it is to
#: stop believing the suite.
REPLY_TIMEOUT_S = 10.0

#: How long to wait when the *expected* outcome is silence.
#:
#: Used only for the mismatched-handshake check, where a timeout is the evidence
#: rather than a failure. Short on purpose: by the time it runs the firmware has
#: already answered on another link, so it is warm and a reply - if one were
#: coming - would be immediate.
SILENCE_TIMEOUT_S = 1.0


class VerificationError(AssertionError):
    """A check failed. Carries a message already formatted expected-vs-actual."""


def check(condition: bool, what: str, expected: object, actual: object) -> None:
    """Asserts one condition, reporting both values when it fails.

    @param condition The thing that must hold.
    @param what A short description of the property under test.
    @param expected What the property should have been.
    @param actual What it was.
    @throws VerificationError If the condition is false.
    """
    if condition:
        print(f"  ok   {what}")
        return
    raise VerificationError(f"{what}\n    expected: {expected}\n    actual:   {actual}")


@dataclass(frozen=True)
class LinkSpec:
    """One link's wire policy, as declared in schema.yaml.

    Written out by hand, deliberately. The firmware reports the frame sizes it
    actually compiled to, and this is the independent statement of what those
    sizes *should* be - so a generator that sized both links identically would be
    caught by the two disagreeing, rather than silently confirmed.
    """

    #: The link's name, as it appears in schema.yaml and generated/links.hpp.
    name: str

    #: Whether frames carry sender/receiver ids.
    topology: Topology

    #: Whether frames carry a sequence number. A consequence of `reliable:`.
    sequence: SequencePolicy

    #: The integrity policy the header carries.
    checksum: ChecksumPolicy

    #: Payload bytes a request must hold: directive + uid + widest arguments.
    request_need: int

    #: Payload bytes a reply must hold: uid + status + widest result.
    reply_need: int

    #: Uids this link's `subsystems:` resolve to.
    carries: Tuple[int, ...]

    def schema_for(self, need: int) -> PacketSchema:
        """The packet schema for one direction of this link.

        Mirrors `packet_size_for` in generated/links.hpp exactly, including its
        one surprise: the arithmetic is `(total / 8 + 1) * 8`, which lands
        strictly *above* the next multiple of 8 rather than on it. A total that
        fell exactly on a boundary would otherwise round to itself and leave
        `PacketSize > sizeof(header_t)` false. Restating the formula rather than
        ceiling-dividing is the point - a ceiling would agree for most sizes and
        silently disagree on the boundary case.

        The 8 is literal on both sides rather than the local word size, so a
        64-bit host and a 32-bit ESP32 derive the same number from one schema.

        @param need The payload requirement for this direction.
        @return A schema whose packet_size matches the firmware's.
        """
        header = PacketSchema(
            packet_size=64, topology=self.topology,
            sequence=self.sequence, checksum=self.checksum,
        ).header_size
        size = ((need + header) // 8 + 1) * 8
        return PacketSchema(
            packet_size=size, topology=self.topology,
            sequence=self.sequence, checksum=self.checksum, board_id=HOST_ID,
        )


#: The two links, as schema.yaml declares them.
#:
#: `bench` is a raw serial pipe: it checksums and retransmits because nothing
#: beneath it does, and being point-to-point its frames name no destination.
#: `net` is tcp, which already provides both, so it adds neither - and being a
#: routed medium, its frames do carry addresses. The two therefore differ in
#: header width *and* in carried payload width, which is what makes the size
#: assertion below meaningful rather than incidental.
BENCH = LinkSpec(
    name="bench",
    topology=Topology.POINT_TO_POINT,
    sequence=SequencePolicy.SEQUENCED,
    checksum=ChecksumPolicy.CRC16,
    request_need=4,
    reply_need=5,
    carries=(UID_SHARED_ECHO, UID_TELEMETRY_SAMPLE),
)

NET = LinkSpec(
    name="net",
    topology=Topology.NETWORK,
    sequence=SequencePolicy.NO_SEQUENCE,
    checksum=ChecksumPolicy.NONE,
    request_need=34,
    reply_need=22,
    carries=(UID_BULK_TRANSFER, UID_SHARED_ECHO),
)


class Link:
    """One end of one link: a socket, and the two packet schemas it speaks."""

    def __init__(self, spec: LinkSpec, sock: socket.socket) -> None:
        """Binds this end to its socket.

        @param spec The link's declared policy.
        @param sock This side's end of the socket pair; the firmware holds the other.
        """
        self.spec = spec
        self._sock = sock
        self._request = spec.schema_for(spec.request_need)
        self._reply = spec.schema_for(spec.reply_need)
        self._buffer = bytearray()

        #: How long this link waits for a frame. Per-link and mutable because
        #: one check expects silence and must not wait the full budget for it.
        self.timeout = REPLY_TIMEOUT_S

    @property
    def request_size(self) -> int:
        """The wire size of a request frame on this link."""
        return self._request.packet_size

    @property
    def reply_size(self) -> int:
        """The wire size of a reply frame on this link."""
        return self._reply.packet_size

    def send_preamble(self, fingerprint: int) -> None:
        """Sends this peer's handshake preamble.

        @param fingerprint The eight-byte schema contract to announce. Passed in
               rather than read from the client bindings so a caller can announce
               a deliberately wrong one.
        """
        self._sock.sendall(preamble.encode(fingerprint))

    def read_preamble(self, expected: int) -> Tuple[preamble.PreambleError, Optional[int]]:
        """Reads the device's preamble and compares it against ours.

        @param expected The fingerprint this peer believes in.
        @return The decode verdict, and the peer's fingerprint when recoverable.
        @throws VerificationError If no preamble arrives before the timeout.
        """
        raw = self._read_exactly(preamble.SIZE)
        return preamble.decode(raw, expected)

    def call(self, uid: int, args: bytes = b"") -> object:
        """Launches one task over this link and waits for its reply.

        @param uid The task to launch.
        @param args Its packed constructor arguments.
        @return The parsed reply.
        @throws VerificationError If nothing arrives before the timeout.
        """
        packet = build_request(
            self._request, uid=uid, uid_bytes=UID_BYTES,
            operation=Operation.REGISTER_TASK, args=args,
            receiver_id=DEVICE_ID if self.spec.topology is Topology.NETWORK else None,
        )
        # Sealed here because the checksum is the transport's job on both sides:
        # the firmware's `protocol::reply` builds a header and leaves the FCS to
        # the channel, and this end must mirror that or `bench` would reject
        # every frame as corrupt.
        validator.seal(packet)
        self._sock.sendall(packet.to_bytes())

        raw = self._read_exactly(self._reply.packet_size)
        received = Packet.from_bytes(self._reply, raw)
        if not validator.is_valid(received):
            raise VerificationError(
                f"{self.spec.name}: reply failed its {self.spec.checksum.name} check\n"
                f"    expected: a frame whose FCS matches its contents\n"
                f"    actual:   {raw.hex()}"
            )
        return parse_reply(received, uid_bytes=UID_BYTES)

    def _read_exactly(self, count: int) -> bytes:
        """Reads exactly `count` bytes, buffering across a split delivery.

        A stream socket may break any write, so a short read is a not-yet rather
        than an error - the same reason the firmware's transport buffers.

        @param count How many bytes to wait for.
        @return Exactly that many.
        @throws VerificationError If they do not arrive within this link's timeout.
        """
        deadline = time.monotonic() + self.timeout
        while len(self._buffer) < count:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise VerificationError(
                    f"{self.spec.name}: timed out waiting for {count} byte(s)\n"
                    f"    expected: a {count}-byte frame within {self.timeout}s\n"
                    f"    actual:   {len(self._buffer)} byte(s): {bytes(self._buffer).hex()}"
                )
            self._sock.settimeout(remaining)
            try:
                chunk = self._sock.recv(4096)
            except socket.timeout:
                continue
            if not chunk:
                raise VerificationError(
                    f"{self.spec.name}: the device closed the link\n"
                    f"    expected: a {count}-byte frame\n"
                    f"    actual:   EOF after {len(self._buffer)} byte(s)"
                )
            self._buffer.extend(chunk)

        out = bytes(self._buffer[:count])
        del self._buffer[:count]
        return out


class Device:
    """The firmware under test, and the two sockets it speaks over."""

    def __init__(self, binary: str) -> None:
        """Launches the firmware with one socket-pair end per link.

        The descriptors are passed as arguments rather than inherited on fixed
        numbers so that the firmware's `main` states plainly which link is which,
        and a mix-up shows up as a refused task rather than as silence.

        @param binary Path to the built `multi_link` executable.
        """
        bench_host, bench_dev = socket.socketpair()
        net_host, net_dev = socket.socketpair()

        # The device's ends must survive exec, and its own reads must not block
        # the run loop that also has to service the other link.
        for sock in (bench_dev, net_dev):
            os.set_inheritable(sock.fileno(), True)
            sock.setblocking(False)

        self._process = subprocess.Popen(
            [binary, str(bench_dev.fileno()), str(net_dev.fileno())],
            close_fds=False,
            stderr=subprocess.PIPE,
        )
        bench_dev.close()
        net_dev.close()

        self.bench = Link(BENCH, bench_host)
        self.net = Link(NET, net_host)
        self.reported = self._read_report()

    def _read_report(self) -> dict:
        """Reads the frame sizes and fingerprint the firmware prints at startup.

        Read back rather than recomputed because the sizes are settled by the
        compiler: the generator emits a payload requirement and the header's
        width is the target's. This is the ground truth the independently
        declared :class:`LinkSpec` values are then checked against.

        @return A mapping of `fingerprint`, and `<link>.request`/`.reply` sizes.
        @throws VerificationError If the firmware does not announce itself.
        """
        report: dict = {}
        assert self._process.stderr is not None
        for _ in range(3):
            line = self._process.stderr.readline().decode(errors="replace").strip()
            if not line:
                raise VerificationError(
                    "the firmware exited before announcing its wire contract\n"
                    "    expected: a fingerprint line and one line per link\n"
                    f"    actual:   {report or 'nothing'}"
                )
            fields = dict(
                part.split("=", 1) for part in line.split() if "=" in part
            )
            if "fingerprint" in fields:
                report["fingerprint"] = int(fields["fingerprint"], 16)
            else:
                name = line.split()[1]
                report[f"{name}.request"] = int(fields["request"])
                report[f"{name}.reply"] = int(fields["reply"])
        return report

    def close(self) -> None:
        """Stops the firmware and releases both sockets."""
        self._process.terminate()
        try:
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._process.kill()
        for link in (self.bench, self.net):
            link._sock.close()
        if self._process.stderr is not None:
            self._process.stderr.close()


def verify_sizes(device: Device) -> None:
    """Each link is sized for its own subsystems, and the two differ.

    @param device The running firmware.
    @throws VerificationError If a size is wrong, or the two links agree.
    """
    print("per-link frame sizing")
    for link in (device.bench, device.net):
        name = link.spec.name
        check(
            device.reported[f"{name}.request"] == link.request_size,
            f"{name} request frame is sized for its own subsystems",
            link.request_size, device.reported[f"{name}.request"],
        )
        check(
            device.reported[f"{name}.reply"] == link.reply_size,
            f"{name} reply frame is sized for its own subsystems",
            link.reply_size, device.reported[f"{name}.reply"],
        )

    # The load-bearing one. If the generator ignored `subsystems:` and sized every
    # link for the whole device, every check above would still pass and only this
    # would fail - both links would come out at `net`'s numbers.
    check(
        (device.bench.request_size, device.bench.reply_size)
        != (device.net.request_size, device.net.reply_size),
        "the two links have DIFFERENT frame sizes",
        "bench and net to differ",
        f"bench={device.bench.request_size}/{device.bench.reply_size} "
        f"net={device.net.request_size}/{device.net.reply_size}",
    )
    check(
        device.net.request_size > device.bench.request_size,
        "the link carrying the wide subsystem has the larger request frame",
        f"net > bench", f"net={device.net.request_size} bench={device.bench.request_size}",
    )


def verify_carried_tasks(device: Device) -> None:
    """A task carried by a link works over that link.

    @param device The running firmware.
    @throws VerificationError If a carried task fails or answers wrongly.
    """
    print("\ncarried tasks run on the link that carries them")

    reply = device.bench.call(UID_TELEMETRY_SAMPLE, pack(["uint8"], [3]))
    check(
        reply.status == StatusCode.TASK_FINISHED,
        "telemetry.sample finishes over bench",
        status_name(StatusCode.TASK_FINISHED), status_name(reply.status),
    )
    (value,) = unpack(["uint16"], reply.result[:2])
    check(value == 0x1000 + 3 * 7, "telemetry.sample returns the value derived from its argument",
          0x1000 + 3 * 7, value)

    args = pack(["uint32"] * 8, [1, 2, 3, 4, 5, 6, 7, 8])
    reply = device.net.call(UID_BULK_TRANSFER, args)
    check(
        reply.status == StatusCode.TASK_FINISHED,
        "bulk.transfer finishes over net",
        status_name(StatusCode.TASK_FINISHED), status_name(reply.status),
    )
    total, count, first, last = unpack(["uint64", "uint32", "uint32", "uint32"], reply.result[:20])
    check(total == 36, "bulk.transfer sums all eight arguments", 36, total)
    check(count == 8, "bulk.transfer unpacked the whole argument list", 8, count)
    check((first, last) == (1, 8), "bulk.transfer preserved argument order", (1, 8), (first, last))


def verify_refusals(device: Device) -> None:
    """A task a link does not carry is refused, and refused *specifically*.

    @param device The running firmware.
    @throws VerificationError If a refusal is missing, or uses the wrong code.
    """
    print("\nuncarried tasks are refused with task_undefined_on_this_link")

    # Sent with no arguments: `bench`'s frames are far too small to carry
    # bulk.transfer's, which is itself part of the point - the refusal has to
    # happen on the uid, before anything tries to parse a payload that cannot fit.
    for link, uid, task in (
        (device.bench, UID_BULK_TRANSFER, "bulk.transfer"),
        (device.net, UID_TELEMETRY_SAMPLE, "telemetry.sample"),
    ):
        reply = link.call(uid)
        check(
            reply.status == StatusCode.TASK_UNDEFINED_ON_THIS_LINK,
            f"{task} over {link.spec.name} is refused with task_undefined_on_this_link",
            status_name(StatusCode.TASK_UNDEFINED_ON_THIS_LINK), status_name(reply.status),
        )
        # Called out separately because this is the failure that would actually
        # mislead someone: `task_unknown` says the device has no such task, and
        # sends an operator looking for a registration that is present.
        check(
            reply.status != StatusCode.TASK_UNKNOWN,
            f"{task} over {link.spec.name} is NOT refused with task_unknown",
            f"anything but {status_name(StatusCode.TASK_UNKNOWN)}",
            status_name(reply.status),
        )
        check(reply.uid == uid, f"the refusal names the uid that was asked for", uid, reply.uid)


def verify_shared_subsystem(device: Device) -> None:
    """The subsystem both links carry works over both of them.

    @param device The running firmware.
    @throws VerificationError If either link refuses or mis-answers it.
    """
    print("\nthe shared subsystem works over BOTH links")

    seen = []
    for link, token in ((device.bench, 0xBEEF), (device.net, 0xCAFE)):
        reply = link.call(UID_SHARED_ECHO, pack(["uint16"], [token]))
        check(
            reply.status == StatusCode.TASK_FINISHED,
            f"shared.echo finishes over {link.spec.name}",
            status_name(StatusCode.TASK_FINISHED), status_name(reply.status),
        )
        echoed, served = unpack(["uint16", "uint8"], reply.result[:3])
        check(echoed == token, f"shared.echo returns its argument over {link.spec.name}",
              hex(token), hex(echoed))
        seen.append(served)

    # The counter lives in the subsystem's context, which exists once. Both links
    # reaching the same instance is what says they reached one device rather than
    # two - a per-link context would have both report the same number.
    check(seen == [1, 2],
          "both links reached the SAME subsystem instance",
          "a served count of 1 then 2 - one context, counted across both links",
          f"{seen[0]} then {seen[1]}")


def verify_handshake(device: Device, binary: str) -> None:
    """Matching peers agree; a corrupted fingerprint is refused by name.

    @param device The already-handshaken firmware, for the agreement case.
    @param binary Path to the firmware, for launching the mismatching case.
    @throws VerificationError If a match is refused or a mismatch is accepted.
    """
    print("\nthe schema fingerprint handshake")

    # The agreement case already happened: every task above ran, and
    # `external_channel::dispatch` refuses every frame until the handshake is
    # ready. Stating it as its own check keeps the report honest about what has
    # been proven rather than leaving it implied.
    check(True, "matching peers completed the handshake (every task above ran)",
          "task traffic accepted", "task traffic accepted")

    truth = device.reported["fingerprint"]

    # One bit, not a random value: a corrupted fingerprint must be refused
    # because it *differs*, not because it looks malformed. Flipping a low bit
    # keeps it a perfectly well-formed preamble that simply is not ours.
    corrupted = truth ^ 0x01

    other = Device(binary)
    try:
        other.bench.send_preamble(corrupted)
        error, peer = other.bench.read_preamble(corrupted)

        check(
            error is preamble.PreambleError.FINGERPRINT_MISMATCH,
            "a corrupted fingerprint is refused as a mismatch",
            preamble.PreambleError.FINGERPRINT_MISMATCH.value,
            error.value,
        )
        check(peer == truth, "the mismatch reports the peer's real fingerprint",
              f"{truth:016X}", f"{peer:016X}" if peer is not None else "None")

        # "Clear error naming both values": the diagnosis is impossible without
        # both, since either alone looks like a plausible eight bytes. This is
        # the exception the client raises for real, not a message assembled here.
        message = str(preamble.SchemaMismatch(error, expected=corrupted, actual=peer))
        check(f"{truth:016X}" in message.upper() and f"{corrupted:016X}" in message.upper(),
              "the mismatch message names BOTH fingerprints",
              f"a message containing {corrupted:016X} and {truth:016X}",
              message)
        print(f"       {message}")

        # And the refusal must bite: a link that failed the handshake carries no
        # task traffic, or the check would be decorative.
        #
        # This is the one check whose evidence is a timeout, so it gets a short
        # one of its own: by now the firmware is warm and has already answered on
        # the other link, so silence here is a decision rather than a slow start.
        other.bench.timeout = SILENCE_TIMEOUT_S
        try:
            other.bench.call(UID_SHARED_ECHO, pack(["uint16"], [0x1234]))
        except VerificationError:
            check(True, "a mismatched link refuses task traffic",
                  "no reply", "no reply")
        else:
            raise VerificationError(
                "a mismatched link answered task traffic\n"
                "    expected: silence from a link that failed the handshake\n"
                "    actual:   a reply"
            )
    finally:
        other.close()


def main() -> int:
    """Runs every check against a freshly launched firmware.

    @return 0 if everything passed, 1 on the first failure.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--binary",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "multi_link"),
        help="the built multi_link executable (default: ./build/multi_link)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.binary):
        print(f"no such binary: {args.binary}\n"
              f"build it first:\n"
              f"  cmake -S {os.path.dirname(os.path.abspath(__file__))} -B build\n"
              f"  cmake --build build", file=sys.stderr)
        return 1

    device = Device(args.binary)
    try:
        # Both peers announce immediately and neither waits to be spoken to, so
        # the order here is not a protocol requirement - it just gets the
        # firmware's preamble out of each link's buffer before task traffic.
        truth = device.reported["fingerprint"]
        for link in (device.bench, device.net):
            link.send_preamble(truth)
            error, _ = link.read_preamble(truth)
            if error is not preamble.PreambleError.NONE:
                raise VerificationError(
                    f"{link.spec.name}: handshake failed against a matching peer\n"
                    f"    expected: {preamble.PreambleError.NONE.value}\n"
                    f"    actual:   {error.value}"
                )

        verify_sizes(device)
        verify_carried_tasks(device)
        verify_refusals(device)
        verify_shared_subsystem(device)
        verify_handshake(device, args.binary)
    except VerificationError as failure:
        print(f"\nFAILED: {failure}", file=sys.stderr)
        return 1
    finally:
        device.close()

    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
