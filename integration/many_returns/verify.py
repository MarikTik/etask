#!/usr/bin/env python3
"""Host-side driver for `integration/many_returns`.

Builds the firmware, runs it, and asserts on every reply frame it produced. The
question being answered is whether a task's ``return {...}`` reaches a peer as
the values it named, in a frame that was sized for them.

Run it::

    python integration/many_returns/verify.py             # build, run, assert
    python integration/many_returns/verify.py --no-build  # assert against an existing build

Exits 0 when every case passes, non-zero on the first failure, and prints
expected against actual for whichever one failed.

## What it decodes with

Nothing here knows the wire format. The reply payload is parsed by
``etask.protocol.parse_reply`` and the result bytes by the *generated* bindings
in ``python/tasks.py`` - the same two pieces a real peer would use. That is
deliberate: a driver with its own decoder would be asserting that two of this
project's files agree with each other, which they would whether or not either
matched the firmware. Here, a codec change that broke the wire breaks this too.

## What it does not test

The transport. The firmware's frames come off its stdout rather than off a
serial port (see ``src/support/loopback_hub.hpp`` for why), so nothing below the
packet is exercised. Framing and delivery are `multi_link`'s subject.
"""

from __future__ import annotations

import argparse
import math
import struct
import subprocess
import sys
from dataclasses import fields as dataclass_fields
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

#: This project's root; every path below is relative to it.
PROJECT = Path(__file__).resolve().parent

#: Where CMake is configured and the binary lands.
BUILD_DIR = PROJECT / "build"

#: The harness executable, named by CMakeLists.txt's `add_executable`.
BINARY = BUILD_DIR / "many_returns"

#: Repository root - three levels up from `integration/many_returns/`. Needed so
#: the generated bindings and the etask runtime can be imported from the
#: checkout rather than from whatever happens to be installed: an integration
#: test that ran against a released client would pass while the branch under it
#: was broken.
REPO = PROJECT.parent.parent

sys.path.insert(0, str(REPO / "etask-python"))
sys.path.insert(0, str(PROJECT / "python"))

from etask.codec import unpack                              # noqa: E402
from etask.protocol import Reply                            # noqa: E402
from etask.status_code import StatusCode, status_name       # noqa: E402

import tasks                                                # noqa: E402


# ----------------------------------------------------------------- expectations

#: The values every task returns, mirroring `src/support/fixtures.hpp`.
#:
#: Deliberately a second, independent copy rather than something parsed out of
#: the C++ header. A test whose expectations are derived from the code under test
#: asserts only that the derivation ran. These are transcribed by hand, and if
#: the two ever disagree that is the test doing its job.
FIXTURES: Dict[str, Any] = {
    "u8": 0xA5,
    "u16": 0xBEEF,
    "u32": 0xDEADBEEF,
    "u64": 0x0123456789ABCDEF,
    "i8": -0x5B,
    "i16": -0x4321,
    "i32": -0x12345678,
    "i64": -0x0123456789ABCDEF,
    "plain_int": -0x0BADF00D,
    "f32": 3.14159274101257324,
    "f64": -2.718281828459045235,
    "yes": True,
    "no": False,
    "wide_base": 1000.5,
    "measure_value": 12.25,
    "measure_variance": 0.0625,
    "measure_samples": 0xC0DE,
    "measure_bus": 0x3C,
    "converge_iterations": 0x11223344,
    "converge_settled": False,
    "classify_label": 0x7E,
    "classify_confidence": 0.875,
    "classify_detail": -0x7EDCBA9876543210,
}

#: The reply payload requirement the generator computed, asserted against the
#: firmware's own view of it.
#:
#: 1 uid + 1 status + 112 for `wide.telemetry`'s fourteen doubles. Written out
#: here rather than read from links.hpp for the same reason as FIXTURES: this is
#: the number the schema *should* produce, and checking it against the number the
#: generator did produce is the whole point. A helper that computed it would
#: reimplement `LinksFile.__reply_need` and agree with it by construction.
EXPECTED_REPLY_PAYLOAD_NEED = 1 + 1 + 14 * 8

#: The status codes the schema keys shapes to, by the name this driver uses for
#: them. `custom(0x71)` has no `StatusCode` member, since it is this project's
#: own code and not one the framework names.
CUSTOM_CLASSIFY = 0x71


class Failure(AssertionError):
    """One case's assertion, with both sides of the comparison in the message."""


def check(label: str, expected: Any, actual: Any) -> None:
    """Asserts two values are equal, naming both when they are not.

    Floats compare exactly. That is intentional and not a rounding oversight:
    every value here is a constant that travelled as fixed-width IEEE-754 bytes
    and was never arithmetic'd on, so anything but bit-equality is a codec fault.
    A tolerance would hide exactly the truncation this project exists to catch -
    a double narrowed to a float still lands within any reasonable epsilon.

    @param label What is being compared, for the failure message.
    @param expected The value the schema and fixtures say should arrive.
    @param actual The value decoded from the frame.
    @raises Failure When they differ.
    """
    if isinstance(expected, float) and isinstance(actual, float):
        same = (expected == actual) or (math.isnan(expected) and math.isnan(actual))
    else:
        # `1 == True` in Python, so a bool checked against an int would pass on a
        # codec that confused the two. Comparing types first closes that.
        same = type(expected) is type(actual) and expected == actual
    if not same:
        raise Failure(
            f"{label}\n"
            f"  expected: {expected!r} ({type(expected).__name__})\n"
            f"  actual:   {actual!r} ({type(actual).__name__})"
        )


# ------------------------------------------------------------------- transcript

class Transcript:
    """The firmware's stdout, parsed into sizes and per-case reply frames.

    The firmware prints one ``case <tag> <hex>`` line per case plus a few
    ``<key> <value>`` size lines, and terminates with ``done``. Parsing is kept
    separate from asserting so a malformed transcript fails as "the run did not
    finish" rather than as a wrong value somewhere in the middle.
    """

    def __init__(self, text: str) -> None:
        """Parses a completed run's output.

        @param text Everything the firmware wrote to stdout.
        @raises Failure When the run did not reach its terminator, which means it
                crashed or hung part-way and every later assertion would be
                asserting against nothing.
        """
        self._sizes: Dict[str, int] = {}
        self._frames: Dict[str, bytes] = {}
        self._order: List[str] = []
        done = False

        for line in text.splitlines():
            parts = line.split()
            if not parts:
                continue
            if parts[0] == "done":
                done = True
            elif parts[0] == "case":
                tag = parts[1]
                # A case with no reply prints its tag and nothing else, which is
                # an empty frame rather than a missing line - so "no reply" is
                # something to assert on rather than an absence to notice.
                self._frames[tag] = bytes.fromhex(parts[2]) if len(parts) > 2 else b""
                self._order.append(tag)
            elif len(parts) == 2:
                self._sizes[parts[0]] = int(parts[1])

        if not done:
            raise Failure(
                "the firmware did not print its 'done' terminator\n"
                f"  expected: a complete run ending in 'done'\n"
                f"  actual:   {len(self._order)} case(s), then nothing"
            )

    def size(self, key: str) -> int:
        """One of the size lines the run opened with.

        @param key The line's name, e.g. ``reply_payload_need``.
        @return Its value.
        @raises Failure When the firmware did not print it.
        """
        if key not in self._sizes:
            raise Failure(f"the firmware printed no '{key}' line")
        return self._sizes[key]

    def reply(self, tag: str) -> Reply:
        """One case's reply, parsed out of its frame.

        @param tag The case's name.
        @return The parsed reply payload: uid, status, and the raw result bytes.
        @raises Failure When the case produced no frame at all, or produced one
                too short to hold a reply header.
        """
        frame = self.frame(tag)
        header = self.size("reply_packet_size") - self.size("reply_payload_size")
        payload = frame[header:]
        uid_bytes = self.size("uid_bytes")
        if len(payload) < uid_bytes + 1:
            raise Failure(
                f"case '{tag}' frame is too short to be a reply\n"
                f"  expected: at least {uid_bytes + 1} payload byte(s)\n"
                f"  actual:   {len(payload)}"
            )
        return Reply(
            uid=int.from_bytes(payload[:uid_bytes], "little"),
            status=payload[uid_bytes],
            result=payload[uid_bytes + 1:],
        )

    def frame(self, tag: str) -> bytes:
        """One case's whole reply frame, header included.

        @param tag The case's name.
        @return The frame's bytes.
        @raises Failure When the case is absent, or replied more than once - the
                harness prints every reply it saw, so a doubled frame means an
                earlier case leaked into this one and reading only the first
                would hide it.
        """
        if tag not in self._frames:
            raise Failure(
                f"case '{tag}' is missing from the transcript\n"
                f"  expected: a 'case {tag} ...' line\n"
                f"  actual:   {', '.join(self._order) or '(no cases)'}"
            )
        frame = self._frames[tag]
        if not frame:
            raise Failure(
                f"case '{tag}' produced no reply\n"
                f"  expected: one reply frame\n"
                f"  actual:   none - the task never completed, or never started"
            )
        expected = self.size("reply_packet_size")
        if len(frame) != expected:
            raise Failure(
                f"case '{tag}' sent {len(frame) // expected} frames, not one\n"
                f"  expected: {expected} bytes\n"
                f"  actual:   {len(frame)}"
            )
        return frame


# ---------------------------------------------------------------------- helpers

def decode(binding: Any, reply: Reply, tag: str) -> Any:
    """Decodes a reply the way the generated client would.

    Goes through the binding's own ``_decode`` rather than unpacking by hand, so
    the shape selection under test is the shipped one: which dataclass a status
    byte maps to is a decision ``TaskBinding`` makes, and reimplementing it here
    would test this file instead.

    @param binding The generated task binding whose SHAPES table applies.
    @param reply The parsed reply payload.
    @param tag The case's name, for the failure message.
    @return The dataclass instance the client would hand a caller.
    @raises Failure When the status matches no declared shape - which for these
            cases means the firmware reported a status the schema never keyed.
    """
    decoded = binding._decode(reply)
    if isinstance(decoded, tasks.UndeclaredResult):
        raise Failure(
            f"case '{tag}' came back with a status no shape is declared for\n"
            f"  expected: one of {sorted(hex(c) for c in binding.SHAPES)}\n"
            f"  actual:   0x{reply.status:02X} ({decoded.status_name})"
        )
    return decoded


def check_shape(tag: str, decoded: Any, expected_type: type, **values: Any) -> None:
    """Asserts a decoded result is the right dataclass with the right fields.

    The type check is the half that matters and the easy one to leave out: a
    task's branches often share a leading field, so a wrong shape whose first
    value happens to be right would pass a value-only comparison.

    @param tag The case's name, for the failure message.
    @param decoded What the binding produced.
    @param expected_type The dataclass the schema says this status carries.
    @param values Field name to expected value, for every field of the shape.
    @raises Failure On a type mismatch, a missing field, or a wrong value.
    """
    check(f"case '{tag}': result shape", expected_type, type(decoded))

    # Every field, not just the ones named: a shape that grew a field the driver
    # forgot would otherwise be tested only in part.
    declared = {field.name for field in dataclass_fields(decoded)}
    if declared != set(values):
        raise Failure(
            f"case '{tag}': the driver checks the wrong field set\n"
            f"  expected: {sorted(declared)}\n"
            f"  actual:   {sorted(values)}"
        )
    for name, expected in values.items():
        check(f"case '{tag}': field '{name}'", expected, getattr(decoded, name))


def check_status(tag: str, reply: Reply, expected: int) -> None:
    """Asserts a reply's status byte, naming both codes when it differs.

    @param tag The case's name.
    @param reply The parsed reply.
    @param expected The status the schema says this branch reports.
    @raises Failure When they differ.
    """
    if reply.status != expected:
        raise Failure(
            f"case '{tag}': status byte\n"
            f"  expected: 0x{expected:02X} ({status_name(expected)})\n"
            f"  actual:   0x{reply.status:02X} ({status_name(reply.status)})"
        )


def check_uid(tag: str, reply: Reply, binding: Any) -> None:
    """Asserts a reply names the task it answers for.

    Cheap, and it catches the failure that would make every other assertion
    meaningless: a reply matched to the wrong task decodes with the wrong shape
    table, and could pass its value checks by coincidence.

    @param tag The case's name.
    @param reply The parsed reply.
    @param binding The task the case addressed.
    @raises Failure When the uid is not the task's.
    """
    check(f"case '{tag}': reply uid", int(binding.UID), reply.uid)


# ------------------------------------------------------------------ the checks

class Checks:
    """Every assertion in the suite, grouped by what it proves.

    A class rather than free functions so each group can be named in the pass
    output and so a new one is added in one place.
    """

    def __init__(self, transcript: Transcript) -> None:
        """@param transcript A completed run's parsed output."""
        self._t = transcript
        # The bindings are built against a null client: nothing here launches
        # anything, it only decodes frames the firmware already produced, and
        # `_decode` never touches the client.
        self._tasks = tasks.Tasks(None)  # type: ignore[arg-type]

    # ------------------------------------------------------------------ sizing

    def frame_sizing(self) -> None:
        """The reply frame is sized for the widest declared shape.

        This is the assertion the whole schema was shaped around: `wide.telemetry`
        is deliberately the single widest shape in the project, so
        `reply_payload_need` has exactly one source and this checks that source
        rather than whichever task happened to be largest.
        """
        need = self._t.size("reply_payload_need")
        check("generated reply_payload_need", EXPECTED_REPLY_PAYLOAD_NEED, need)

        # And that the frame actually built from it can carry it. The generator
        # computes the requirement; a `constexpr` in links.hpp turns it into a
        # packet size by adding the header and rounding up. Nothing in C++
        # asserts the result is big enough, so this does.
        payload = self._t.size("reply_payload_size")
        if payload < need:
            raise Failure(
                "the reply packet cannot carry its own payload requirement\n"
                f"  expected: payload_size >= {need}\n"
                f"  actual:   {payload}"
            )

        # The widest result must fit with the uid and status byte in front of it.
        # Stated separately from the line above because it is a different claim:
        # that the *result region*, not the payload, has room for 112 bytes.
        uid_bytes = self._t.size("uid_bytes")
        region = payload - uid_bytes - 1
        widest = 14 * 8
        if region < widest:
            raise Failure(
                "the reply's result region is smaller than the widest shape\n"
                f"  expected: >= {widest} bytes for wide.telemetry\n"
                f"  actual:   {region}"
            )

    # ----------------------------------------------------------------- scalars

    def scalars(self) -> None:
        """Every type in TypeMap round-trips byte-exactly."""
        self._unsigned_widths()
        self._signed_widths()
        self._plain_int()
        self._reals()
        self._flags()
        self._positional()

    def _unsigned_widths(self) -> None:
        """uint8/16/32/64, ascending, in one shape."""
        tag = "unsigned_widths"
        binding = self._tasks.scalars.unsigned_widths
        reply = self._t.reply(tag)
        check_uid(tag, reply, binding)
        check_status(tag, reply, StatusCode.TASK_FINISHED)
        check_shape(
            tag, decode(binding, reply, tag), binding.Finished,
            u8=FIXTURES["u8"], u16=FIXTURES["u16"],
            u32=FIXTURES["u32"], u64=FIXTURES["u64"],
        )

    def _signed_widths(self) -> None:
        """int8/16/32/64, all negative, so sign extension is exercised."""
        tag = "signed_widths"
        binding = self._tasks.scalars.signed_widths
        reply = self._t.reply(tag)
        check_uid(tag, reply, binding)
        check_status(tag, reply, StatusCode.TASK_FINISHED)
        check_shape(
            tag, decode(binding, reply, tag), binding.Finished,
            i8=FIXTURES["i8"], i16=FIXTURES["i16"],
            i32=FIXTURES["i32"], i64=FIXTURES["i64"],
        )

    def _plain_int(self) -> None:
        """The bare `int` spelling, distinct from `int32` in the schema."""
        tag = "plain_int"
        binding = self._tasks.scalars.plain_int
        reply = self._t.reply(tag)
        check_uid(tag, reply, binding)
        check_status(tag, reply, StatusCode.TASK_FINISHED)
        check_shape(
            tag, decode(binding, reply, tag), binding.Finished,
            value=FIXTURES["plain_int"],
        )

    def _reals(self) -> None:
        """float and double side by side, at values neither width shares."""
        tag = "reals"
        binding = self._tasks.scalars.reals
        reply = self._t.reply(tag)
        check_uid(tag, reply, binding)
        check_status(tag, reply, StatusCode.TASK_FINISHED)
        decoded = decode(binding, reply, tag)

        # The float is compared against its own single-precision rounding, not
        # against the literal: the firmware stored it in a `float`, so the value
        # on the wire is the nearest float to the constant and expecting the
        # decimal itself would fail on a correct implementation. The double is
        # compared exactly - it lost nothing.
        f32 = struct.unpack("<f", struct.pack("<f", FIXTURES["f32"]))[0]
        check_shape(tag, decoded, binding.Finished, f32=f32, f64=FIXTURES["f64"])

    def _flags(self) -> None:
        """bool, both ways, in one byte each."""
        tag = "flags"
        binding = self._tasks.scalars.flags
        reply = self._t.reply(tag)
        check_uid(tag, reply, binding)
        check_status(tag, reply, StatusCode.TASK_FINISHED)
        # `getattr` for `no`: it is a Python keyword-adjacent name only by luck,
        # but `yes`/`no` come straight from the schema and the dataclass carries
        # them verbatim.
        check_shape(
            tag, decode(binding, reply, tag), binding.Finished,
            yes=FIXTURES["yes"], no=FIXTURES["no"],
        )

    def _positional(self) -> None:
        """A positionally-declared shape is the same wire format as a named one.

        The generated dataclass names these fields ``v0``..``v4`` because the
        schema gave them no names, but the bytes are indistinguishable from a
        named shape of the same types. Proving that is the point of the task: the
        two spellings are one wire contract, and only the binding differs.
        """
        tag = "positional"
        binding = self._tasks.scalars.positional
        reply = self._t.reply(tag)
        check_uid(tag, reply, binding)
        check_status(tag, reply, StatusCode.TASK_FINISHED)
        check_shape(
            tag, decode(binding, reply, tag), binding.Finished,
            v0=FIXTURES["u8"], v1=FIXTURES["i16"], v2=FIXTURES["u32"],
            v3=FIXTURES["f64"], v4=FIXTURES["yes"],
        )

        # And the bytes themselves, decoded as an anonymous tuple rather than
        # through the shape table. If the positional form ever gained a length
        # prefix or a name tag, the dataclass check above would still pass -
        # `unpack` ignores trailing bytes - and this would not.
        types = ("uint8", "int16", "uint32", "double", "bool")
        raw = unpack(types, reply.result)
        check(
            f"case '{tag}': raw positional decode",
            (FIXTURES["u8"], FIXTURES["i16"], FIXTURES["u32"],
             FIXTURES["f64"], FIXTURES["yes"]),
            raw,
        )

    # ------------------------------------------------------------ empty results

    def empty_results(self) -> None:
        """A task that returns nothing still replies, carrying its status."""
        self._acknowledge()
        self._report_status()

    def _acknowledge(self) -> None:
        """No `returns:` at all: the manager's own status, and no bytes."""
        tag = "acknowledge"
        binding = self._tasks.nothing.acknowledge
        reply = self._t.reply(tag)
        check_uid(tag, reply, binding)
        check_status(tag, reply, StatusCode.TASK_FINISHED)

        # The task declared no shape, so there is nothing for the bindings to
        # decode into and `UndeclaredResult` is the correct answer rather than a
        # failure. That is worth asserting explicitly: it is the one place in this
        # suite where an undeclared result is right.
        decoded = binding._decode(reply)
        check(
            f"case '{tag}': decoded type",
            tasks.UndeclaredResult, type(decoded),
        )

        # The result region is the frame's zero-fill, since the task wrote
        # nothing into it. Asserting it is *all* zero is what distinguishes "the
        # task returned nothing" from "the task returned something the driver
        # cannot see".
        if any(decoded.raw):
            raise Failure(
                f"case '{tag}': a task with no declared result wrote bytes\n"
                f"  expected: all zero\n"
                f"  actual:   {decoded.raw.hex()}"
            )

    def _report_status(self) -> None:
        """Two declared-but-empty shapes, told apart only by the status byte."""
        binding = self._tasks.nothing.report_status
        for tag, expected_status, shape in (
            ("report_io_error", StatusCode.TASK_IO_ERROR, binding.IoError),
            ("report_timeout", StatusCode.TASK_TIMEOUT, binding.Timeout),
        ):
            reply = self._t.reply(tag)
            check_uid(tag, reply, binding)
            check_status(tag, reply, expected_status)
            # No fields to compare - which is exactly why this case exists. The
            # shape is the whole assertion: the status byte alone selected it.
            check_shape(tag, decode(binding, reply, tag), shape)

    # -------------------------------------------------------------------- wide

    def widest_shape(self) -> None:
        """The 112-byte shape arrives whole, with no truncation and no reordering.

        A `result_too_large` here would be the headline failure this project is
        looking for: it would mean the generator sized a frame the schema's own
        widest declaration does not fit into.
        """
        tag = "telemetry"
        binding = self._tasks.wide.telemetry
        reply = self._t.reply(tag)
        check_uid(tag, reply, binding)

        if reply.status == StatusCode.RESULT_TOO_LARGE:
            raise Failure(
                f"case '{tag}': the widest declared result did not fit its frame\n"
                f"  expected: 0x{int(StatusCode.TASK_FINISHED):02X} (task_finished) "
                f"with {14 * 8} result bytes\n"
                f"  actual:   0x{reply.status:02X} (result_too_large), no result. "
                "The generator sized this frame from this very shape, so this is a "
                "generator bug, not a schema one."
            )
        check_status(tag, reply, StatusCode.TASK_FINISHED)

        expected = {
            f"d{i}": FIXTURES["wide_base"] + float(i) for i in range(14)
        }
        check_shape(tag, decode(binding, reply, tag), binding.Finished, **expected)

        # Every channel differs from its neighbours by construction, so a decode
        # that were one slot out would fail above. This asserts the complement:
        # that nothing was written *past* the fourteenth channel, which a shape
        # occupying the frame's full result region could hide.
        written = 14 * 8
        if any(reply.result[written:]):
            raise Failure(
                f"case '{tag}': bytes written past the declared shape\n"
                f"  expected: zero-fill after {written} bytes\n"
                f"  actual:   {reply.result[written:].hex()}"
            )

    # ------------------------------------------------------------ status-keyed

    def status_keyed(self) -> None:
        """Each branch of each multi-shape task is reachable and decodes right."""
        self._measure()
        self._converge()
        self._classify()

    def _measure(self) -> None:
        """Three branches, eighteen bytes down to zero, all steered by a param."""
        binding = self._tasks.keyed.measure

        tag = "measure_finished"
        reply = self._t.reply(tag)
        check_uid(tag, reply, binding)
        check_status(tag, reply, StatusCode.TASK_FINISHED)
        check_shape(
            tag, decode(binding, reply, tag), binding.Finished,
            value=FIXTURES["measure_value"],
            variance=FIXTURES["measure_variance"],
            samples=FIXTURES["measure_samples"],
        )

        tag = "measure_io_error"
        reply = self._t.reply(tag)
        check_uid(tag, reply, binding)
        check_status(tag, reply, StatusCode.TASK_IO_ERROR)
        check_shape(
            tag, decode(binding, reply, tag), binding.IoError,
            bus=FIXTURES["measure_bus"],
        )
        # The narrow branch travels in the same frame as the wide one, so the
        # seventeen bytes after its single value are zero-fill. A peer that
        # decoded by length rather than by status would read them as a reading.
        if any(reply.result[1:]):
            raise Failure(
                f"case '{tag}': bytes past the io_error shape's one byte\n"
                f"  expected: zero-fill\n"
                f"  actual:   {reply.result[1:].hex()}"
            )

        tag = "measure_timeout"
        reply = self._t.reply(tag)
        check_uid(tag, reply, binding)
        check_status(tag, reply, StatusCode.TASK_TIMEOUT)
        check_shape(tag, decode(binding, reply, tag), binding.Timeout)
        if any(reply.result):
            raise Failure(
                f"case '{tag}': the empty branch wrote bytes\n"
                f"  expected: all zero\n"
                f"  actual:   {reply.result.hex()}"
            )

        # And the branches really are different shapes, not one shape reported
        # under three statuses. Comparing their declared widths is the check that
        # would fail if a schema edit accidentally made them agree, which would
        # quietly turn every assertion above into a tautology.
        widths = {
            code: sum(
                {"uint8": 1, "uint16": 2, "double": 8}[t] for t in types
            )
            for code, (_, types) in binding.SHAPES.items()
        }
        check(
            "keyed.measure branch widths",
            {int(StatusCode.TASK_FINISHED): 18,
             int(StatusCode.TASK_TIMEOUT): 0,
             int(StatusCode.TASK_IO_ERROR): 1},
            widths,
        )

    def _converge(self) -> None:
        """The abort branch, reachable only by force-completing the task.

        `keyed.converge` never finishes on its own, so its `finished` shape is
        unreachable from the wire and `aborted` is the branch a peer can provoke.
        The status is the manager's own rather than one the task named, which is
        the case worth separating: a shape can be keyed to a status no
        `with_status` call ever produces.
        """
        tag = "converge_aborted"
        binding = self._tasks.keyed.converge
        reply = self._t.reply(tag)
        check_uid(tag, reply, binding)
        check_status(tag, reply, StatusCode.TASK_ABORTED)
        check_shape(
            tag, decode(binding, reply, tag), binding.Aborted,
            # The task echoes the target it was started with, so this proves the
            # request's argument survived the round trip too.
            last=FIXTURES["i32"],
            iterations=FIXTURES["converge_iterations"],
            settled=FIXTURES["converge_settled"],
        )

        # The two branches must not be confusable: `finished` is four bytes and
        # `aborted` is nine, so a reply decoded under the wrong one would read
        # `iterations` out of `last`'s bytes and look plausible.
        check(
            f"case '{tag}': the two branches differ in width",
            True,
            len(binding.SHAPES[int(StatusCode.TASK_FINISHED)][1])
            != len(binding.SHAPES[int(StatusCode.TASK_ABORTED)][1]),
        )

    def _classify(self) -> None:
        """A custom status code keys its own shape, above the task range."""
        binding = self._tasks.keyed.classify

        tag = "classify_finished"
        reply = self._t.reply(tag)
        check_uid(tag, reply, binding)
        check_status(tag, reply, StatusCode.TASK_FINISHED)
        check_shape(
            tag, decode(binding, reply, tag), binding.Finished,
            label=FIXTURES["classify_label"],
        )

        tag = "classify_custom"
        reply = self._t.reply(tag)
        check_uid(tag, reply, binding)
        check_status(tag, reply, CUSTOM_CLASSIFY)
        # A custom code sits above the framework's range, so the one thing that
        # must not happen is its being read as a manager rejection - which the
        # client raises on rather than decodes. Reaching the shape at all is the
        # assertion; the values confirm it is the right one.
        if reply.is_rejection:
            raise Failure(
                f"case '{tag}': a custom status was read as a manager rejection\n"
                f"  expected: 0x{CUSTOM_CLASSIFY:02X} treated as a completion\n"
                f"  actual:   is_rejection is True"
            )
        check_shape(
            tag, decode(binding, reply, tag), binding.Custom71,
            label=FIXTURES["classify_label"],
            confidence=FIXTURES["classify_confidence"],
            detail=FIXTURES["classify_detail"],
        )

        # Both branches open with the same `label`, so the status byte is the
        # only thing that could have selected between them. Asserting that they
        # share the prefix is what makes the two checks above meaningful.
        check(
            "keyed.classify branches share their first field",
            binding.SHAPES[int(StatusCode.TASK_FINISHED)][1],
            binding.SHAPES[CUSTOM_CLASSIFY][1][:1],
        )


# ----------------------------------------------------------------------- runner

def build() -> None:
    """Configures and builds the firmware.

    @raises SystemExit When CMake or the compiler fails; its output has already
            been shown, so there is nothing to add.
    """
    for command in (
        ["cmake", "-S", str(PROJECT), "-B", str(BUILD_DIR)],
        ["cmake", "--build", str(BUILD_DIR)],
    ):
        result = subprocess.run(command)
        if result.returncode != 0:
            raise SystemExit(result.returncode)


def run_firmware() -> str:
    """Runs the harness and returns its transcript.

    @return Everything the firmware wrote to stdout.
    @raises Failure When the binary is missing, exits non-zero, or does not
            terminate - each of which is a different problem and says so.
    """
    if not BINARY.exists():
        raise Failure(
            f"the harness binary is missing\n"
            f"  expected: {BINARY}\n"
            f"  actual:   not built - drop --no-build, or build it yourself"
        )
    try:
        result = subprocess.run(
            [str(BINARY)], capture_output=True, text=True, timeout=60
        )
    except subprocess.TimeoutExpired:
        raise Failure(
            "the harness did not terminate within 60s\n"
            "  expected: a single pass over every case, then exit\n"
            "  actual:   still running - a task is most likely never finishing"
        )
    if result.returncode != 0:
        raise Failure(
            f"the harness exited {result.returncode}\n"
            f"  expected: 0\n"
            f"  actual:   {result.returncode}\n{result.stderr}"
        )
    return result.stdout


#: Every check, in the order they run. Ordered so a failure lands on the most
#: specific thing wrong: sizing first, because a mis-sized frame makes every
#: value assertion misleading, then values, then the shape dispatch built on them.
SUITE: Sequence[Tuple[str, str]] = (
    ("frame_sizing", "the reply frame is sized for the widest declared shape"),
    ("scalars", "every scalar type round-trips byte-exactly"),
    ("empty_results", "a task returning nothing still replies with its status"),
    ("widest_shape", "the widest shape arrives whole"),
    ("status_keyed", "every branch of every status-keyed task decodes correctly"),
)


def main() -> int:
    """Builds, runs, and asserts.

    @return 0 when every check passes, 1 on the first failure.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-build", action="store_true",
        help="assert against an existing build instead of rebuilding first",
    )
    args = parser.parse_args()

    if not args.no_build:
        build()

    try:
        checks = Checks(Transcript(run_firmware()))
        for name, description in SUITE:
            getattr(checks, name)()
            print(f"  ok  {description}")
    except Failure as failure:
        print(f"\nFAILED: {failure}", file=sys.stderr)
        return 1

    print(f"\n{len(SUITE)} check group(s) passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
