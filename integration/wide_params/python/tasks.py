"""Generated etask client bindings - do not edit.

Regenerated from the project's schema on every `etask generate --python`
run; 20 task(s).

Each task is an awaitable call whose result is one of its declared
shapes, chosen by the status code the reply carries::

    async with Client(channel, uid_bytes=UID_BYTES,
                      fingerprint=SCHEMA_FINGERPRINT) as client:
        tasks = Tasks(client)
        result = await tasks.<scope>.<task>(<params>)

Launching does not block: start several tasks and await them together
with `asyncio.gather`. See `etask.client` for how replies are matched.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from etask.binding import (
    InstantTaskBinding,
    Scope,
    TaskBinding,
    UndeclaredResult,
    build_shapes,
)
from etask.client import Client

UID_BYTES = 1
"""Width of a task uid on the wire, pinned by the project's uid ledger."""

SCHEMA_FINGERPRINT = 0xBC0623D1BD50D54C
"""The wire contract this client speaks, as eight bytes.

Covers every uid, argument list, result shape and link policy in the
schema this was generated from. The device sends its own at connect; if
the two differ, the peers were built from different schemas and the
client refuses the link rather than trading frames whose uids it would
misread.
"""


class TaskId(IntEnum):
    """Every task's wire uid - the same values as `global::task_id` in C++."""

    ECHO_ECHO_BOOL = 68
    ECHO_ECHO_INT8 = 196
    ECHO_ECHO_UINT8 = 124
    ECHO_ECHO_INT16 = 113
    ECHO_ECHO_UINT16 = 66
    ECHO_ECHO_INT32 = 20
    ECHO_ECHO_UINT32 = 75
    ECHO_ECHO_INT64 = 136
    ECHO_ECHO_UINT64 = 187
    ECHO_ECHO_FLOAT = 36
    ECHO_ECHO_DOUBLE = 84
    ECHO_ECHO_INT = 112
    MIXED_SANDWICH = 159
    MIXED_STAIRCASE = 157
    MIXED_AVALANCHE = 109
    MIXED_ODD_PAIR = 222
    MIXED_SIGNED_RUN = 57
    WIDE_EVERYTHING = 100
    WIDE_SATURATED = 21
    WIDE_FOLDED_MIXED = 101




@dataclass(frozen=True)
class EchoEchoBoolFinished:
    """`echo.echo_bool` result carried by `finished` (0x20)."""

    v: bool


class _EchoEchoBool(TaskBinding):
    """echo a bool

    Schema path `echo.echo_bool`, uid 68.

    Returns one of:
      - `EchoEchoBoolFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ECHO_ECHO_BOOL
    PATH = "echo.echo_bool"
    PARAMS = ("bool",)
    SHAPES = build_shapes([
        (0x20, EchoEchoBoolFinished, ("bool",)),
    ])

    Finished = EchoEchoBoolFinished

    async def __call__(self, *, v: bool) -> EchoEchoBoolFinished | UndeclaredResult:
        """Starts `echo.echo_bool` and waits for its reply.

        Args:
            v: `bool`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([v])


@dataclass(frozen=True)
class EchoEchoInt8Finished:
    """`echo.echo_int8` result carried by `finished` (0x20)."""

    v: int


class _EchoEchoInt8(TaskBinding):
    """echo an int8

    Schema path `echo.echo_int8`, uid 196.

    Returns one of:
      - `EchoEchoInt8Finished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ECHO_ECHO_INT8
    PATH = "echo.echo_int8"
    PARAMS = ("int8",)
    SHAPES = build_shapes([
        (0x20, EchoEchoInt8Finished, ("int8",)),
    ])

    Finished = EchoEchoInt8Finished

    async def __call__(self, *, v: int) -> EchoEchoInt8Finished | UndeclaredResult:
        """Starts `echo.echo_int8` and waits for its reply.

        Args:
            v: `int8`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([v])


@dataclass(frozen=True)
class EchoEchoUint8Finished:
    """`echo.echo_uint8` result carried by `finished` (0x20)."""

    v: int


class _EchoEchoUint8(TaskBinding):
    """echo a uint8

    Schema path `echo.echo_uint8`, uid 124.

    Returns one of:
      - `EchoEchoUint8Finished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ECHO_ECHO_UINT8
    PATH = "echo.echo_uint8"
    PARAMS = ("uint8",)
    SHAPES = build_shapes([
        (0x20, EchoEchoUint8Finished, ("uint8",)),
    ])

    Finished = EchoEchoUint8Finished

    async def __call__(self, *, v: int) -> EchoEchoUint8Finished | UndeclaredResult:
        """Starts `echo.echo_uint8` and waits for its reply.

        Args:
            v: `uint8`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([v])


@dataclass(frozen=True)
class EchoEchoInt16Finished:
    """`echo.echo_int16` result carried by `finished` (0x20)."""

    v: int


class _EchoEchoInt16(TaskBinding):
    """echo an int16

    Schema path `echo.echo_int16`, uid 113.

    Returns one of:
      - `EchoEchoInt16Finished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ECHO_ECHO_INT16
    PATH = "echo.echo_int16"
    PARAMS = ("int16",)
    SHAPES = build_shapes([
        (0x20, EchoEchoInt16Finished, ("int16",)),
    ])

    Finished = EchoEchoInt16Finished

    async def __call__(self, *, v: int) -> EchoEchoInt16Finished | UndeclaredResult:
        """Starts `echo.echo_int16` and waits for its reply.

        Args:
            v: `int16`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([v])


@dataclass(frozen=True)
class EchoEchoUint16Finished:
    """`echo.echo_uint16` result carried by `finished` (0x20)."""

    v: int


class _EchoEchoUint16(TaskBinding):
    """echo a uint16

    Schema path `echo.echo_uint16`, uid 66.

    Returns one of:
      - `EchoEchoUint16Finished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ECHO_ECHO_UINT16
    PATH = "echo.echo_uint16"
    PARAMS = ("uint16",)
    SHAPES = build_shapes([
        (0x20, EchoEchoUint16Finished, ("uint16",)),
    ])

    Finished = EchoEchoUint16Finished

    async def __call__(self, *, v: int) -> EchoEchoUint16Finished | UndeclaredResult:
        """Starts `echo.echo_uint16` and waits for its reply.

        Args:
            v: `uint16`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([v])


@dataclass(frozen=True)
class EchoEchoInt32Finished:
    """`echo.echo_int32` result carried by `finished` (0x20)."""

    v: int


class _EchoEchoInt32(TaskBinding):
    """echo an int32

    Schema path `echo.echo_int32`, uid 20.

    Returns one of:
      - `EchoEchoInt32Finished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ECHO_ECHO_INT32
    PATH = "echo.echo_int32"
    PARAMS = ("int32",)
    SHAPES = build_shapes([
        (0x20, EchoEchoInt32Finished, ("int32",)),
    ])

    Finished = EchoEchoInt32Finished

    async def __call__(self, *, v: int) -> EchoEchoInt32Finished | UndeclaredResult:
        """Starts `echo.echo_int32` and waits for its reply.

        Args:
            v: `int32`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([v])


@dataclass(frozen=True)
class EchoEchoUint32Finished:
    """`echo.echo_uint32` result carried by `finished` (0x20)."""

    v: int


class _EchoEchoUint32(TaskBinding):
    """echo a uint32

    Schema path `echo.echo_uint32`, uid 75.

    Returns one of:
      - `EchoEchoUint32Finished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ECHO_ECHO_UINT32
    PATH = "echo.echo_uint32"
    PARAMS = ("uint32",)
    SHAPES = build_shapes([
        (0x20, EchoEchoUint32Finished, ("uint32",)),
    ])

    Finished = EchoEchoUint32Finished

    async def __call__(self, *, v: int) -> EchoEchoUint32Finished | UndeclaredResult:
        """Starts `echo.echo_uint32` and waits for its reply.

        Args:
            v: `uint32`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([v])


@dataclass(frozen=True)
class EchoEchoInt64Finished:
    """`echo.echo_int64` result carried by `finished` (0x20)."""

    v: int


class _EchoEchoInt64(TaskBinding):
    """echo an int64

    Schema path `echo.echo_int64`, uid 136.

    Returns one of:
      - `EchoEchoInt64Finished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ECHO_ECHO_INT64
    PATH = "echo.echo_int64"
    PARAMS = ("int64",)
    SHAPES = build_shapes([
        (0x20, EchoEchoInt64Finished, ("int64",)),
    ])

    Finished = EchoEchoInt64Finished

    async def __call__(self, *, v: int) -> EchoEchoInt64Finished | UndeclaredResult:
        """Starts `echo.echo_int64` and waits for its reply.

        Args:
            v: `int64`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([v])


@dataclass(frozen=True)
class EchoEchoUint64Finished:
    """`echo.echo_uint64` result carried by `finished` (0x20)."""

    v: int


class _EchoEchoUint64(TaskBinding):
    """echo a uint64

    Schema path `echo.echo_uint64`, uid 187.

    Returns one of:
      - `EchoEchoUint64Finished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ECHO_ECHO_UINT64
    PATH = "echo.echo_uint64"
    PARAMS = ("uint64",)
    SHAPES = build_shapes([
        (0x20, EchoEchoUint64Finished, ("uint64",)),
    ])

    Finished = EchoEchoUint64Finished

    async def __call__(self, *, v: int) -> EchoEchoUint64Finished | UndeclaredResult:
        """Starts `echo.echo_uint64` and waits for its reply.

        Args:
            v: `uint64`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([v])


@dataclass(frozen=True)
class EchoEchoFloatFinished:
    """`echo.echo_float` result carried by `finished` (0x20)."""

    v: float


class _EchoEchoFloat(TaskBinding):
    """echo a float

    Schema path `echo.echo_float`, uid 36.

    Returns one of:
      - `EchoEchoFloatFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ECHO_ECHO_FLOAT
    PATH = "echo.echo_float"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, EchoEchoFloatFinished, ("float",)),
    ])

    Finished = EchoEchoFloatFinished

    async def __call__(self, *, v: float) -> EchoEchoFloatFinished | UndeclaredResult:
        """Starts `echo.echo_float` and waits for its reply.

        Args:
            v: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([v])


@dataclass(frozen=True)
class EchoEchoDoubleFinished:
    """`echo.echo_double` result carried by `finished` (0x20)."""

    v: float


class _EchoEchoDouble(TaskBinding):
    """echo a double

    Schema path `echo.echo_double`, uid 84.

    Returns one of:
      - `EchoEchoDoubleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ECHO_ECHO_DOUBLE
    PATH = "echo.echo_double"
    PARAMS = ("double",)
    SHAPES = build_shapes([
        (0x20, EchoEchoDoubleFinished, ("double",)),
    ])

    Finished = EchoEchoDoubleFinished

    async def __call__(self, *, v: float) -> EchoEchoDoubleFinished | UndeclaredResult:
        """Starts `echo.echo_double` and waits for its reply.

        Args:
            v: `double`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([v])


@dataclass(frozen=True)
class EchoEchoIntFinished:
    """`echo.echo_int` result carried by `finished` (0x20)."""

    v: int


class _EchoEchoInt(TaskBinding):
    """echo an `int` (the schema's alias for int32)

    Schema path `echo.echo_int`, uid 112.

    Returns one of:
      - `EchoEchoIntFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ECHO_ECHO_INT
    PATH = "echo.echo_int"
    PARAMS = ("int",)
    SHAPES = build_shapes([
        (0x20, EchoEchoIntFinished, ("int",)),
    ])

    Finished = EchoEchoIntFinished

    async def __call__(self, *, v: int) -> EchoEchoIntFinished | UndeclaredResult:
        """Starts `echo.echo_int` and waits for its reply.

        Args:
            v: `int`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([v])


@dataclass(frozen=True)
class MixedSandwichFinished:
    """`mixed.sandwich` result carried by `finished` (0x20)."""

    head: int
    body: float
    tail: int


class _MixedSandwich(TaskBinding):
    """uint8, double, uint8 - the canonical padding trap

    Schema path `mixed.sandwich`, uid 159.

    Returns one of:
      - `MixedSandwichFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MIXED_SANDWICH
    PATH = "mixed.sandwich"
    PARAMS = ("uint8", "double", "uint8")
    SHAPES = build_shapes([
        (0x20, MixedSandwichFinished, ("uint8", "double", "uint8")),
    ])

    Finished = MixedSandwichFinished

    async def __call__(self, *, head: int, body: float, tail: int) -> MixedSandwichFinished | UndeclaredResult:
        """Starts `mixed.sandwich` and waits for its reply.

        Args:
            head: `uint8`.
            body: `double`.
            tail: `uint8`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([head, body, tail])


@dataclass(frozen=True)
class MixedStaircaseFinished:
    """`mixed.staircase` result carried by `finished` (0x20)."""

    a: int
    b: int
    c: int
    d: int


class _MixedStaircase(TaskBinding):
    """widths ascending 1,2,4,8 - every field naturally aligned

    Schema path `mixed.staircase`, uid 157.

    Returns one of:
      - `MixedStaircaseFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MIXED_STAIRCASE
    PATH = "mixed.staircase"
    PARAMS = ("uint8", "uint16", "uint32", "uint64")
    SHAPES = build_shapes([
        (0x20, MixedStaircaseFinished, ("uint8", "uint16", "uint32", "uint64")),
    ])

    Finished = MixedStaircaseFinished

    async def __call__(self, *, a: int, b: int, c: int, d: int) -> MixedStaircaseFinished | UndeclaredResult:
        """Starts `mixed.staircase` and waits for its reply.

        Args:
            a: `uint8`.
            b: `uint16`.
            c: `uint32`.
            d: `uint64`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([a, b, c, d])


@dataclass(frozen=True)
class MixedAvalancheFinished:
    """`mixed.avalanche` result carried by `finished` (0x20)."""

    a: int
    b: int
    c: int
    d: int
    e: int
    f: int
    g: int


class _MixedAvalanche(TaskBinding):
    """widths descending 8,4,2,1 then ascending again

    Schema path `mixed.avalanche`, uid 109.

    Returns one of:
      - `MixedAvalancheFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MIXED_AVALANCHE
    PATH = "mixed.avalanche"
    PARAMS = ("uint64", "uint32", "uint16", "uint8", "uint16", "uint32", "uint64")
    SHAPES = build_shapes([
        (0x20, MixedAvalancheFinished, ("uint64", "uint32", "uint16", "uint8", "uint16", "uint32", "uint64")),
    ])

    Finished = MixedAvalancheFinished

    async def __call__(self, *, a: int, b: int, c: int, d: int, e: int, f: int, g: int) -> MixedAvalancheFinished | UndeclaredResult:
        """Starts `mixed.avalanche` and waits for its reply.

        Args:
            a: `uint64`.
            b: `uint32`.
            c: `uint16`.
            d: `uint8`.
            e: `uint16`.
            f: `uint32`.
            g: `uint64`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([a, b, c, d, e, f, g])


@dataclass(frozen=True)
class MixedOddPairFinished:
    """`mixed.odd_pair` result carried by `finished` (0x20)."""

    flag: bool
    wide: float
    other: bool
    narrow: float


class _MixedOddPair(TaskBinding):
    """bool, double, bool, float - the two floating widths off-alignment

    Schema path `mixed.odd_pair`, uid 222.

    Returns one of:
      - `MixedOddPairFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MIXED_ODD_PAIR
    PATH = "mixed.odd_pair"
    PARAMS = ("bool", "double", "bool", "float")
    SHAPES = build_shapes([
        (0x20, MixedOddPairFinished, ("bool", "double", "bool", "float")),
    ])

    Finished = MixedOddPairFinished

    async def __call__(self, *, flag: bool, wide: float, other: bool, narrow: float) -> MixedOddPairFinished | UndeclaredResult:
        """Starts `mixed.odd_pair` and waits for its reply.

        Args:
            flag: `bool`.
            wide: `double`.
            other: `bool`.
            narrow: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([flag, wide, other, narrow])


@dataclass(frozen=True)
class MixedSignedRunFinished:
    """`mixed.signed_run` result carried by `finished` (0x20)."""

    a: int
    b: int
    c: int
    d: int
    e: int
    f: int
    g: int
    h: int


class _MixedSignedRun(TaskBinding):
    """alternating signed and unsigned at every width

    Schema path `mixed.signed_run`, uid 57.

    Returns one of:
      - `MixedSignedRunFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MIXED_SIGNED_RUN
    PATH = "mixed.signed_run"
    PARAMS = ("int8", "uint8", "int16", "uint16", "int32", "uint32", "int64", "uint64")
    SHAPES = build_shapes([
        (0x20, MixedSignedRunFinished, ("int8", "uint8", "int16", "uint16", "int32", "uint32", "int64", "uint64")),
    ])

    Finished = MixedSignedRunFinished

    async def __call__(self, *, a: int, b: int, c: int, d: int, e: int, f: int, g: int, h: int) -> MixedSignedRunFinished | UndeclaredResult:
        """Starts `mixed.signed_run` and waits for its reply.

        Args:
            a: `int8`.
            b: `uint8`.
            c: `int16`.
            d: `uint16`.
            e: `int32`.
            f: `uint32`.
            g: `int64`.
            h: `uint64`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([a, b, c, d, e, f, g, h])


@dataclass(frozen=True)
class WideEverythingFinished:
    """`wide.everything` result carried by `finished` (0x20)."""

    b: bool
    i8: int
    u8: int
    i16: int
    u16: int
    i32: int
    u32: int
    i64: int
    u64: int
    f: float
    d: float
    n: int


class _WideEverything(TaskBinding):
    """every scalar type once, in one call

    Schema path `wide.everything`, uid 100.

    Returns one of:
      - `WideEverythingFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.WIDE_EVERYTHING
    PATH = "wide.everything"
    PARAMS = ("bool", "int8", "uint8", "int16", "uint16", "int32", "uint32", "int64", "uint64", "float", "double", "int")
    SHAPES = build_shapes([
        (0x20, WideEverythingFinished, ("bool", "int8", "uint8", "int16", "uint16", "int32", "uint32", "int64", "uint64", "float", "double", "int")),
    ])

    Finished = WideEverythingFinished

    async def __call__(self, *, b: bool, i8: int, u8: int, i16: int, u16: int, i32: int, u32: int, i64: int, u64: int, f: float, d: float, n: int) -> WideEverythingFinished | UndeclaredResult:
        """Starts `wide.everything` and waits for its reply.

        Args:
            b: `bool`.
            i8: `int8`.
            u8: `uint8`.
            i16: `int16`.
            u16: `uint16`.
            i32: `int32`.
            u32: `uint32`.
            i64: `int64`.
            u64: `uint64`.
            f: `float`.
            d: `double`.
            n: `int`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([b, i8, u8, i16, u16, i32, u32, i64, u64, f, d, n])


@dataclass(frozen=True)
class WideSaturatedFinished:
    """`wide.saturated` result carried by `finished` (0x20)."""

    digest: int


class _WideSaturated(TaskBinding):
    """six doubles - the widest single-type list, folded on return

    Schema path `wide.saturated`, uid 21.

    Returns one of:
      - `WideSaturatedFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.WIDE_SATURATED
    PATH = "wide.saturated"
    PARAMS = ("double", "double", "double", "double", "double", "double")
    SHAPES = build_shapes([
        (0x20, WideSaturatedFinished, ("uint64",)),
    ])

    Finished = WideSaturatedFinished

    async def __call__(self, *, a: float, b: float, c: float, d: float, e: float, f: float) -> WideSaturatedFinished | UndeclaredResult:
        """Starts `wide.saturated` and waits for its reply.

        Args:
            a: `double`.
            b: `double`.
            c: `double`.
            d: `double`.
            e: `double`.
            f: `double`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([a, b, c, d, e, f])


@dataclass(frozen=True)
class WideFoldedMixedFinished:
    """`wide.folded_mixed` result carried by `finished` (0x20)."""

    digest: int


class _WideFoldedMixed(TaskBinding):
    """a wide mixed list, folded over the raw argument bytes

    Schema path `wide.folded_mixed`, uid 101.

    Returns one of:
      - `WideFoldedMixedFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.WIDE_FOLDED_MIXED
    PATH = "wide.folded_mixed"
    PARAMS = ("uint8", "double", "uint8", "int64", "bool", "float", "int16", "uint32")
    SHAPES = build_shapes([
        (0x20, WideFoldedMixedFinished, ("uint64",)),
    ])

    Finished = WideFoldedMixedFinished

    async def __call__(self, *, u8: int, d: float, u8b: int, i64: int, b: bool, f: float, i16: int, u32: int) -> WideFoldedMixedFinished | UndeclaredResult:
        """Starts `wide.folded_mixed` and waits for its reply.

        Args:
            u8: `uint8`.
            d: `double`.
            u8b: `uint8`.
            i64: `int64`.
            b: `bool`.
            f: `float`.
            i16: `int16`.
            u32: `uint32`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([u8, d, u8b, i64, b, f, i16, u32])


class _WideScope(Scope):
    """the widest parameter lists a frame carries

    Schema scope `wide`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.everything = _WideEverything(client)
        self.saturated = _WideSaturated(client)
        self.folded_mixed = _WideFoldedMixed(client)


class _MixedScope(Scope):
    """narrow and wide types interleaved, in padding-hostile orders

    Schema scope `mixed`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sandwich = _MixedSandwich(client)
        self.staircase = _MixedStaircase(client)
        self.avalanche = _MixedAvalanche(client)
        self.odd_pair = _MixedOddPair(client)
        self.signed_run = _MixedSignedRun(client)


class _EchoScope(Scope):
    """one task per scalar type, echoed back unchanged

    Schema scope `echo`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.echo_bool = _EchoEchoBool(client)
        self.echo_int8 = _EchoEchoInt8(client)
        self.echo_uint8 = _EchoEchoUint8(client)
        self.echo_int16 = _EchoEchoInt16(client)
        self.echo_uint16 = _EchoEchoUint16(client)
        self.echo_int32 = _EchoEchoInt32(client)
        self.echo_uint32 = _EchoEchoUint32(client)
        self.echo_int64 = _EchoEchoInt64(client)
        self.echo_uint64 = _EchoEchoUint64(client)
        self.echo_float = _EchoEchoFloat(client)
        self.echo_double = _EchoEchoDouble(client)
        self.echo_int = _EchoEchoInt(client)


class Tasks(Scope):
    """The project's task tree, mirroring the schema's scopes.

    Construct it with a live `Client`; every task below is an
    awaitable call at the same path the schema declares.
    """

    UID_BYTES = UID_BYTES

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.echo = _EchoScope(client)
        self.mixed = _MixedScope(client)
        self.wide = _WideScope(client)
