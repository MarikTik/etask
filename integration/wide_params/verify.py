#!/usr/bin/env python3
"""Host driver for the `wide_params` integration project.

Calls every task in `schema.yaml` with values chosen to break a serializer,
and asserts on what comes back. Exits 0 only if every byte of every round trip
survived; on any mismatch it prints what differed and exits 1.

## What this is actually testing

Not "does the device work". The wire codec is flat, tagless and positional -
nothing on the wire says what a byte means - so a host and a device that
disagree by one byte of width, one byte of padding, or one bit of endianness
still exchange frames that parse cleanly and mean different things. There is no
checksum failure and no exception; there is a plausible-looking wrong answer.

The only way to see that is to send values whose every byte is distinguishable
and compare what comes back, which is what this file does. The device half is
`src/sys/`, whose tasks echo their arguments rather than computing anything.

## Choosing the values

A test that sends 1, 2, 3 passes on a byte-swapped link, because 1 and 2 and 3
are their own low bytes. Every value here is picked so that a *specific* bug
changes it:

    endianness      0x0102030405060708 and friends - every byte differs, so a
                    swap of any width is visible and not symmetric.
    truncation      type maxima and minima - the values that stop fitting the
                    moment a width shrinks.
    sign            -1, and each signed type's minimum - a signedness mistake
                    turns -1 into that type's maximum, which is as far away as
                    the type allows.
    float widening  doubles whose low mantissa bits are set, so a double that
                    passed through a float comes back a different number.
    float narrowing floats that are *exactly* representable, so a mismatch is
                    the transport's fault and never the test's rounding.
    zero            0 and False, because a zeroed frame is what a device that
                    never answered looks like, and it must not be mistaken for
                    a correct answer to a question whose answer is zero.

## Running it

    ./verify.py --port /dev/ttyUSB0

    ./verify.py --self-test        # no board: check the vectors and the fold

`--self-test` is what CI's hosted jobs run. It exercises everything in this file
that does not need a device - the value table, the codec round trip through
`etask.codec`, and the fold that `src/support/fold.hpp` has to agree with - so a
broken driver is caught by the same push that broke it, rather than by the next
person who plugs a board in.
"""

from __future__ import annotations

import argparse
import asyncio
import math
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

# The generated client lives beside this file, under python/. It is an output of
# the same `etask generate` run that produced the firmware's src/generated, which
# is what makes the two ends agree; importing it from anywhere else would be
# importing a different contract.
sys.path.insert(0, str(Path(__file__).resolve().parent / "python"))

from etask.codec import pack, unpack  # noqa: E402


# ---------------------------------------------------------------------------
# The fold that two tasks answer with
# ---------------------------------------------------------------------------

#: FNV-1a's 64-bit offset basis and prime. Named rather than inlined because
#: `src/support/fold.hpp` declares the same two constants and the pair has to
#: match; a literal in each file is a literal to get wrong in one of them.
FNV_OFFSET_BASIS = 0xCBF29CE484222325
FNV_PRIME = 0x00000100000001B3
_U64 = 0xFFFFFFFFFFFFFFFF


def fold(types: Sequence[str], values: Sequence[Any]) -> int:
    """Computes the digest `wide.saturated` and `wide.folded_mixed` must return.

    This function is normative: `src/support/fold.hpp` exists to reproduce it
    on the device, and the two must agree bit for bit. Change neither alone.

    The bytes folded are each value's *declared* wire width, which is the whole
    point. A device that widened a `uint8` argument to a word before folding it
    contributes four bytes where this contributes one, and disagrees - while
    every echo task still passes, because an echo shows what a value was and
    never how it was held between being unpacked and packed again.

    @param types Schema type names, in the schema's declared order.
    @param values The argument values, in the same order.
    @return The 64-bit digest.
    """
    digest = FNV_OFFSET_BASIS
    for type_name, value in zip(types, values):
        # pack() one value at a time, so each contributes exactly its own wire
        # width - packing the list in one call would give the same bytes today
        # but would silently follow the codec if it ever grew alignment.
        for byte in pack([type_name], [value]):
            digest = ((digest ^ byte) * FNV_PRIME) & _U64
    return digest


# ---------------------------------------------------------------------------
# The values
# ---------------------------------------------------------------------------

#: Per-type test vectors, each chosen against a specific failure. Every list
#: leads with 0 - a zeroed frame is indistinguishable from a device that never
#: wrote one, so "zero survives" has to be asserted rather than assumed.
VECTORS: dict[str, list[Any]] = {
    "bool": [False, True],
    "int8": [0, 1, -1, 127, -128, 0x55, -0x56],
    "uint8": [0, 1, 0xFF, 0x80, 0x0F, 0xF0],
    "int16": [0, 1, -1, 32767, -32768, 0x0102, -0x0102],
    "uint16": [0, 1, 0xFFFF, 0x0102, 0x8000, 0x00FF, 0xFF00],
    # 0x01020304 is the endianness canary: every byte differs, so a swap of any
    # width lands on a value that is not in this list.
    "int32": [0, 1, -1, 2147483647, -2147483648, 0x01020304, -0x01020304],
    "uint32": [0, 1, 0xFFFFFFFF, 0x01020304, 0x80000000, 0x0000FFFF],
    "int64": [0, 1, -1, 2**63 - 1, -(2**63), 0x0102030405060708, -0x0102030405060708],
    "uint64": [0, 1, 2**64 - 1, 0x0102030405060708, 2**63, 0x00000000FFFFFFFF],
    # Every float here is exactly representable in 24 bits of mantissa, so a
    # mismatch is the wire's doing and never this file rounding. The subnormal
    # and the maximum are the two a naive double<->float shim loses.
    "float": [0.0, -0.0, 1.0, -1.0, 0.5, -0.5,
              3.4028234663852886e38,      # FLT_MAX
              1.1754943508222875e-38,     # FLT_MIN, the smallest normal
              float(0x00FFFFFF)],         # the largest exactly-integral float
    # Each of these needs more than 24 bits of mantissa, so a `double` that was
    # quietly demoted to `float` anywhere on the path comes back different.
    # That demotion is a real toolchain default, not a hypothetical.
    "double": [0.0, -0.0, 1.0, -1.0,
               1.7976931348623157e308,    # DBL_MAX
               2.2250738585072014e-308,   # DBL_MIN, the smallest normal
               math.pi,
               1.0000000000000002,        # 1 + one ulp: a float rounds it to 1.0
               float(2**53 - 1)],         # the largest exactly-integral double
    "int": [0, 1, -1, 2147483647, -2147483648, 0x01020304],
}


@dataclass(frozen=True)
class Mismatch:
    """One field that came back wrong.

    @param task The dotted schema path of the task that was called.
    @param field The result field's name, or `digest` for a folding task.
    @param sent What the driver asked for.
    @param got What the device answered.
    """

    task: str
    field: str
    sent: Any
    got: Any

    def __str__(self) -> str:
        return (f"  {self.task}.{self.field}: "
                f"sent {_show(self.sent)}, got {_show(self.got)}")


def _show(value: Any) -> str:
    """Renders a value so a wrong one is *readable as* wrong.

    Integers get hex alongside decimal, because a byte swap is obvious in hex
    and invisible in decimal. Floats get their exact bit pattern, because two
    doubles that print identically at repr precision can still differ in the
    low mantissa bits - which is exactly the truncation this driver hunts, and
    a report that printed both as "3.141592653589793" would hide it.

    @param value The value to render.
    @return A string naming the value unambiguously.
    """
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return f"{value} (0x{value & _U64:X})" if value else "0"
    if isinstance(value, float):
        bits = struct.unpack("<Q", struct.pack("<d", value))[0]
        return f"{value!r} (bits 0x{bits:016X})"
    return repr(value)


def _same(sent: Any, got: Any) -> bool:
    """Whether a returned value is the one that was sent, bit for bit.

    Floats are compared by their bit pattern rather than by `==`. Two reasons,
    and both matter here: `-0.0 == 0.0` is true while the two differ in the
    sign bit, and a NaN is equal to nothing including itself. Neither would be
    a *correct* round trip, so equality is the wrong test even though it is the
    obvious one.

    @param sent The value the driver sent.
    @param got The value the device returned.
    @return True if they are identical.
    """
    if isinstance(sent, float) and isinstance(got, float):
        return struct.pack("<d", sent) == struct.pack("<d", got)
    return type(sent) is type(got) and sent == got


# ---------------------------------------------------------------------------
# The calls
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Call:
    """One planned invocation: a task, its arguments, and what it must answer.

    @param path The dotted schema path, used in the report.
    @param binding Resolves the bound task off a live `Tasks` tree.
    @param types The parameter type names, in the schema's order.
    @param args Argument name -> value.
    @param folded Whether the reply is a digest rather than an echo.
    """

    path: str
    binding: Callable[[Any], Any]
    types: tuple[str, ...]
    args: dict[str, Any]
    folded: bool = False

    def expected(self) -> dict[str, Any]:
        """What the reply's fields must contain.

        @return Field name -> required value: the arguments themselves for an
                echoing task, or the single digest for a folding one.
        """
        if self.folded:
            return {"digest": fold(self.types, list(self.args.values()))}
        return dict(self.args)


def _echo_calls() -> list[Call]:
    """Every per-type echo call: one task per schema type, one call per vector.

    @return The calls, in schema order.
    """
    calls: list[Call] = []
    for type_name, values in VECTORS.items():
        task = f"echo_{type_name}"
        for value in values:
            calls.append(Call(
                path=f"echo.{task}",
                binding=lambda tasks, t=task: getattr(tasks.echo, t),
                types=(type_name,),
                args={"v": value},
            ))
    return calls


def _mixed_calls() -> list[Call]:
    """The padding-hostile orderings, each driven to its types' extremes.

    Extremes rather than middling values because padding shows up as bytes read
    from the wrong offset: a field that borrowed a neighbour's bytes looks
    plausible when the neighbours are small, and unmistakable when they are
    saturated.

    @return The calls, in schema order.
    """
    return [
        Call("mixed.sandwich", lambda t: t.mixed.sandwich,
             ("uint8", "double", "uint8"),
             {"head": 0xA5, "body": math.pi, "tail": 0x5A}),
        Call("mixed.sandwich", lambda t: t.mixed.sandwich,
             ("uint8", "double", "uint8"),
             {"head": 0xFF, "body": 1.7976931348623157e308, "tail": 0xFF}),
        # Zero in the middle: the one case where a device that dropped the
        # double entirely would still return something that looks right, so the
        # neighbours are saturated to make the drop visible anyway.
        Call("mixed.sandwich", lambda t: t.mixed.sandwich,
             ("uint8", "double", "uint8"),
             {"head": 0xFF, "body": 0.0, "tail": 0xFF}),

        Call("mixed.staircase", lambda t: t.mixed.staircase,
             ("uint8", "uint16", "uint32", "uint64"),
             {"a": 0x01, "b": 0x0203, "c": 0x04050607, "d": 0x08090A0B0C0D0E0F}),
        Call("mixed.staircase", lambda t: t.mixed.staircase,
             ("uint8", "uint16", "uint32", "uint64"),
             {"a": 0xFF, "b": 0xFFFF, "c": 0xFFFFFFFF, "d": 2**64 - 1}),

        Call("mixed.avalanche", lambda t: t.mixed.avalanche,
             ("uint64", "uint32", "uint16", "uint8", "uint16", "uint32", "uint64"),
             {"a": 0x0102030405060708, "b": 0x090A0B0C, "c": 0x0D0E, "d": 0x0F,
              "e": 0x1011, "f": 0x12131415, "g": 0x161718191A1B1C1D}),

        Call("mixed.odd_pair", lambda t: t.mixed.odd_pair,
             ("bool", "double", "bool", "float"),
             {"flag": True, "wide": 1.0000000000000002,
              "other": False, "narrow": float(0x00FFFFFF)}),
        Call("mixed.odd_pair", lambda t: t.mixed.odd_pair,
             ("bool", "double", "bool", "float"),
             {"flag": False, "wide": -0.0, "other": True, "narrow": -0.0}),

        # Signed fields at their minima and unsigned at their maxima: the two
        # halves of a signedness mistake, so whichever way it goes it shows.
        Call("mixed.signed_run", lambda t: t.mixed.signed_run,
             ("int8", "uint8", "int16", "uint16",
              "int32", "uint32", "int64", "uint64"),
             {"a": -128, "b": 0xFF, "c": -32768, "d": 0xFFFF,
              "e": -2147483648, "f": 0xFFFFFFFF, "g": -(2**63), "h": 2**64 - 1}),
        Call("mixed.signed_run", lambda t: t.mixed.signed_run,
             ("int8", "uint8", "int16", "uint16",
              "int32", "uint32", "int64", "uint64"),
             {"a": -1, "b": 1, "c": -1, "d": 1,
              "e": -1, "f": 1, "g": -1, "h": 1}),
    ]


def _wide_calls() -> list[Call]:
    """The widest lists: `everything` echoed, the two folding tasks digested.

    @return The calls, in schema order.
    """
    every_types = ("bool", "int8", "uint8", "int16", "uint16", "int32",
                   "uint32", "int64", "uint64", "float", "double", "int")
    saturated_types = ("double",) * 6
    folded_types = ("uint8", "double", "uint8", "int64",
                    "bool", "float", "int16", "uint32")

    return [
        Call("wide.everything", lambda t: t.wide.everything, every_types,
             {"b": True, "i8": -128, "u8": 0xFF, "i16": -32768, "u16": 0xFFFF,
              "i32": -2147483648, "u32": 0xFFFFFFFF, "i64": 0x0102030405060708,
              "u64": 2**64 - 1, "f": float(0x00FFFFFF),
              "d": 1.0000000000000002, "n": 0x01020304}),
        # The all-zero call. Nothing here distinguishes a correct answer from a
        # device that replied with an empty frame - which is why it is worth
        # sending: it is the one case where the reply's *length* is doing the
        # work, and a truncated result would decode as this and pass. Paired
        # with the saturated call above, a device that always returns zeros
        # fails one and a device that always echoes fails neither.
        Call("wide.everything", lambda t: t.wide.everything, every_types,
             {"b": False, "i8": 0, "u8": 0, "i16": 0, "u16": 0,
              "i32": 0, "u32": 0, "i64": 0, "u64": 0,
              "f": 0.0, "d": 0.0, "n": 0}),

        Call("wide.saturated", lambda t: t.wide.saturated, saturated_types,
             {"a": math.pi, "b": -math.e, "c": 1.7976931348623157e308,
              "d": 2.2250738585072014e-308, "e": 1.0000000000000002, "f": -0.0},
             folded=True),
        Call("wide.saturated", lambda t: t.wide.saturated, saturated_types,
             dict.fromkeys("abcdef", 0.0), folded=True),

        Call("wide.folded_mixed", lambda t: t.wide.folded_mixed, folded_types,
             {"u8": 0xA5, "d": math.pi, "u8b": 0x5A, "i64": -(2**63),
              "b": True, "f": float(0x00FFFFFF), "i16": -32768,
              "u32": 0xFFFFFFFF},
             folded=True),
        Call("wide.folded_mixed", lambda t: t.wide.folded_mixed, folded_types,
             {"u8": 0, "d": 0.0, "u8b": 0, "i64": 0,
              "b": False, "f": 0.0, "i16": 0, "u32": 0},
             folded=True),
    ]


def plan() -> list[Call]:
    """Every call this driver makes, in schema order.

    @return The full call list.
    """
    return _echo_calls() + _mixed_calls() + _wide_calls()


# ---------------------------------------------------------------------------
# Checking a reply
# ---------------------------------------------------------------------------

def check(call: Call, result: Any) -> list[Mismatch]:
    """Compares one reply against what the call required.

    @param call The call that was made.
    @param result Whatever the binding returned - a result dataclass, or an
           `UndeclaredResult` if the device answered with a status the schema
           declares no shape for.
    @return The mismatches found; empty if the round trip was exact.
    """
    expected = call.expected()

    # An UndeclaredResult has no fields to compare, so it is one mismatch for
    # the whole call rather than one per field: the device did not answer the
    # question, so there is nothing to say about the individual values.
    if not all(hasattr(result, field) for field in expected):
        return [Mismatch(call.path, "<shape>",
                         f"a reply carrying {', '.join(expected)}",
                         type(result).__name__)]

    return [Mismatch(call.path, field, want, getattr(result, field))
            for field, want in expected.items()
            if not _same(want, getattr(result, field))]


# ---------------------------------------------------------------------------
# Self-test: everything that does not need a board
# ---------------------------------------------------------------------------

def self_test() -> list[str]:
    """Checks this driver against itself, with no device present.

    Three things, all of which can be wrong without a board being involved:

    - every vector survives `etask.codec`'s own pack/unpack, so a failure
      against real hardware is the *device's* and not this file's;
    - every planned call's arguments match its declared types in count and
      order, which is what a hand-written call list gets wrong;
    - the fold is stable and actually depends on width, so a device that
      matched it by accident could not.

    @return Descriptions of what failed; empty if everything held.
    """
    failures: list[str] = []

    for type_name, values in VECTORS.items():
        for value in values:
            (got,) = unpack([type_name], pack([type_name], [value]))
            if not _same(value, got):
                failures.append(
                    f"codec round trip failed for {type_name}: "
                    f"{_show(value)} -> {_show(got)}")

    for call in plan():
        if len(call.types) != len(call.args):
            failures.append(
                f"{call.path}: {len(call.types)} type(s) but "
                f"{len(call.args)} argument(s) - {list(call.args)}")
            continue
        try:
            pack(list(call.types), list(call.args.values()))
        except Exception as error:                        # noqa: BLE001
            failures.append(f"{call.path}: arguments do not pack - {error}")

    # Width sensitivity: the same numeric value at two widths must not fold to
    # the same digest. If it did, the fold would be measuring the value rather
    # than its representation, and the truncation bug would walk straight past.
    if fold(("uint8",), (1,)) == fold(("uint32",), (1,)):
        failures.append("fold() is width-blind: uint8 1 and uint32 1 agree")
    if fold(("float",), (1.0,)) == fold(("double",), (1.0,)):
        failures.append("fold() is width-blind: float 1.0 and double 1.0 agree")

    return failures


# ---------------------------------------------------------------------------
# The transport
# ---------------------------------------------------------------------------

class AsyncSerialChannel:
    """An asyncio serial channel, which ecomm-python does not ship.

    `ecomm.channels` has `SerialChannel` (synchronous) and `AsyncTcpChannel`
    (asynchronous), but nothing that is both serial and async - and
    `etask.client.Client` requires async, because its whole design is that a
    launch does not block. Rather than make this driver synchronous and give up
    the ability to have several tasks in flight, it wraps pyserial's blocking
    reads in the default executor.

    This belongs in ecomm-python, not here. It lives in this file because a
    driver is the wrong place to add a framework class, and because doing it
    here keeps the change that adds it properly a separate one.
    """

    def __init__(self, schema: Any, port: str, baudrate: int) -> None:
        """Opens the port.

        @param schema The `ecomm.protocol.schema.PacketSchema` frames are built
               against; must match the device's, which `generated/links.hpp`
               fixes.
        @param port OS device path, e.g. `/dev/ttyUSB0`.
        @param baudrate Bits per second. Must equal `app::link_baud` in
               src/app.cpp exactly - a mismatch reads as corruption, not silence.
        """
        import serial                                     # noqa: PLC0415

        from ecomm.channels.async_base import AsyncChannel  # noqa: PLC0415

        self._base = AsyncChannel
        self.schema = schema
        # A short timeout rather than none: a read that blocks forever pins an
        # executor thread that nothing can cancel, so the port is polled and the
        # coroutine yields between polls.
        self._port = serial.Serial(port=port, baudrate=baudrate, timeout=0.05)
        self._buffer = bytearray()

    async def _read_exactly(self, size: int) -> bytes:
        """Reads exactly `size` bytes, suspending until they arrive.

        @param size How many bytes to return.
        @return Exactly that many bytes.
        """
        loop = asyncio.get_running_loop()
        while len(self._buffer) < size:
            chunk = await loop.run_in_executor(
                None, self._port.read, size - len(self._buffer))
            if chunk:
                self._buffer.extend(chunk)
            else:
                await asyncio.sleep(0)
        out = bytes(self._buffer[:size])
        del self._buffer[:size]
        return out

    async def send_raw(self, data: bytes) -> None:
        """Writes bytes outside any frame - the handshake preamble's path.

        @param data The bytes to write.
        """
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._port.write, data)

    async def read_raw(self, size: int) -> bytes:
        """Reads up to `size` bytes without waiting for a full frame.

        The handshake needs this: it is looking for a 14-byte preamble in a
        stream whose framing has not been established yet, so it cannot ask for
        a packet.

        @param size Maximum bytes to return.
        @return What was available, possibly empty.
        """
        loop = asyncio.get_running_loop()
        if self._buffer:
            out = bytes(self._buffer[:size])
            del self._buffer[:size]
            return out
        return await loop.run_in_executor(None, self._port.read, size)

    async def unread_raw(self, data: bytes) -> None:
        """Puts bytes back that the handshake over-read.

        On a stream transport the bytes past the preamble are the start of the
        first real frame and there is nobody else to recover them.

        @param data The bytes to push back.
        """
        self._buffer[:0] = data


def open_channel(port: str, baudrate: int) -> Any:
    """Builds the channel for this project's one link.

    The packet geometry is not chosen here: it is read off `generated/links.hpp`,
    which computed it from the schema. Hand-writing it would put a copy of the
    numbers this project exists to check on the checking side.

    @param port OS device path.
    @param baudrate Bits per second.
    @return An open channel bound to the `bench` link's reply geometry.
    """
    from ecomm.channels.async_base import AsyncChannel     # noqa: PLC0415
    from ecomm.protocol.checksum import ChecksumPolicy     # noqa: PLC0415
    from ecomm.protocol.schema import PacketSchema         # noqa: PLC0415
    from ecomm.protocol.sequence import SequencePolicy     # noqa: PLC0415
    from ecomm.protocol.topology import Topology           # noqa: PLC0415

    # `bench` in schema.yaml: uart, so point_to_point, crc16 and reliable all
    # come from the transport's defaults. See generated/links.hpp, which spells
    # out each one and why.
    schema = PacketSchema(
        packet_size=_reply_packet_size(),
        topology=Topology.POINT_TO_POINT,
        sequence=SequencePolicy.SEQUENCED,
        checksum=ChecksumPolicy.CRC16,
    )

    channel = AsyncSerialChannel(schema, port, baudrate)
    # AsyncSerialChannel is a duck-typed AsyncChannel rather than a subclass, so
    # that the import of ecomm stays inside the functions that need it - this
    # file must import and self-test with no ecomm and no pyserial installed.
    AsyncChannel.__init__(channel, schema)
    return channel


def _reply_packet_size() -> int:
    """The `bench` link's reply frame size, read out of generated/links.hpp.

    Parsed from the generated header rather than restated, so that a schema
    change resizes both ends together. The alternative - a constant here - is
    the exact class of drift this project was built to catch, and it would be
    perverse for the driver to introduce one.

    @return The reply packet size in bytes.
    @throws RuntimeError If the header cannot be read or does not name a size.
    """
    header = Path(__file__).resolve().parent / "src" / "generated" / "links.hpp"
    try:
        text = header.read_text()
    except OSError as error:
        raise RuntimeError(
            f"cannot read {header}: run the generator first "
            "(cmake --build build --target app-etask-generate)") from error

    marker = "inline constexpr std::size_t reply_payload_need = "
    at = text.find(marker)
    if at < 0:
        raise RuntimeError(f"{header} declares no reply_payload_need")
    need = int(text[at + len(marker):text.index(";", at)])

    # The header's own arithmetic: payload + header, rounded to the next
    # multiple of 8 strictly above it. See `packet_size_for` in links.hpp for
    # why the 8 is a literal and not sizeof(size_t).
    header_size = 1 + 1 + 2        # protocol byte + sequence + crc16, no node ids
    return ((need + header_size) // 8 + 1) * 8


# ---------------------------------------------------------------------------
# Driving the device
# ---------------------------------------------------------------------------

async def run(port: str, baudrate: int, receiver_id: int) -> list[Mismatch]:
    """Makes every planned call against a live device and collects the failures.

    Calls are made one at a time and awaited. That is deliberate and not
    laziness: several in flight would prove concurrency, which is
    `bombardment`'s subject, while here it would only add a second explanation
    for a wrong answer - the client matches replies to launches FIFO per uid,
    so overlapping two calls to the same task could pair a reply with the wrong
    launch and report a mismatch that is the harness's fault.

    @param port OS device path.
    @param baudrate Bits per second; must match the firmware.
    @param receiver_id The device's ecomm node id.
    @return Every mismatch found, across every call.
    """
    from etask.client import Client                        # noqa: PLC0415

    import tasks as generated                              # noqa: PLC0415

    channel = open_channel(port, baudrate)
    mismatches: list[Mismatch] = []

    async with Client(channel,
                      uid_bytes=generated.Tasks.UID_BYTES,
                      receiver_id=receiver_id,
                      fingerprint=generated.SCHEMA_FINGERPRINT) as client:
        tasks = generated.Tasks(client)
        for call in plan():
            result = await call.binding(tasks)(**call.args)
            mismatches.extend(check(call, result))

    return mismatches


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def report(failures: Iterable[str]) -> int:
    """Prints failures and returns the process exit status.

    @param failures Human-readable descriptions, one per failure.
    @return 0 if there were none, 1 otherwise.
    """
    listed = list(failures)
    if not listed:
        return 0
    print(f"FAIL: {len(listed)} mismatch(es)", file=sys.stderr)
    for line in listed:
        print(line, file=sys.stderr)
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Parses arguments and runs either the self-test or the device run.

    @param argv Command-line arguments, or None for `sys.argv`.
    @return The process exit status: 0 on success, non-zero on any mismatch.
    """
    parser = argparse.ArgumentParser(
        description="Round-trip every scalar type against a wide_params device.")
    parser.add_argument("--port", default="/dev/ttyUSB0",
                        help="serial device the board is on (default: %(default)s)")
    parser.add_argument("--baud", type=int, default=115200,
                        help="must equal app::link_baud in src/app.cpp "
                             "(default: %(default)s)")
    parser.add_argument("--receiver-id", type=int, default=1,
                        help="the device's ecomm node id; matches ECOMM_BOARD_ID "
                             "(default: %(default)s)")
    parser.add_argument("--self-test", action="store_true",
                        help="check the vectors, the call list and the fold "
                             "without a board, then exit")
    args = parser.parse_args(argv)

    if args.self_test:
        failures = self_test()
        if not failures:
            print(f"ok: {len(plan())} call(s) planned, "
                  f"{sum(len(v) for v in VECTORS.values())} vector(s) checked")
        return report(failures)

    # The self-test is not optional before a real run: if the vectors or the
    # call list are wrong, every device mismatch reported afterwards would be
    # this file's fault, and the report would send someone hunting a firmware
    # bug that is not there.
    broken = self_test()
    if broken:
        print("refusing to run against a device: the driver itself is wrong",
              file=sys.stderr)
        return report(broken)

    mismatches = asyncio.run(run(args.port, args.baud, args.receiver_id))
    if not mismatches:
        print(f"ok: {len(plan())} call(s), every byte round-tripped")
    return report(str(m) for m in mismatches)


if __name__ == "__main__":
    sys.exit(main())
