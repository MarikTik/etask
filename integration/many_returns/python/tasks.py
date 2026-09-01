"""Generated etask client bindings - do not edit.

Regenerated from the project's schema on every `etask generate --python`
run; 12 task(s).

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

SCHEMA_FINGERPRINT = 0xACC3121AB2AB7AD3
"""The wire contract this client speaks, as eight bytes.

Covers every uid, argument list, result shape and link policy in the
schema this was generated from. The device sends its own at connect; if
the two differ, the peers were built from different schemas and the
client refuses the link rather than trading frames whose uids it would
misread.
"""


class TaskId(IntEnum):
    """Every task's wire uid - the same values as `global::task_id` in C++."""

    NOTHING_ACKNOWLEDGE = 107
    NOTHING_REPORT_STATUS = 156
    SCALARS_UNSIGNED_WIDTHS = 230
    SCALARS_SIGNED_WIDTHS = 200
    SCALARS_PLAIN_INT = 50
    SCALARS_REALS = 252
    SCALARS_FLAGS = 235
    SCALARS_POSITIONAL = 94
    WIDE_TELEMETRY = 0
    KEYED_MEASURE = 113
    KEYED_CONVERGE = 253
    KEYED_CLASSIFY = 192




class _NothingAcknowledge(TaskBinding):
    """complete naturally, carrying no result

    Schema path `nothing.acknowledge`, uid 107.
    """

    UID = TaskId.NOTHING_ACKNOWLEDGE
    PATH = "nothing.acknowledge"
    PARAMS = ()
    SHAPES = {}

    async def __call__(self) -> UndeclaredResult:
        """Starts `nothing.acknowledge` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class NothingReportStatusTimeout:
    """`nothing.report_status` result carried by `task_timeout` (0x22)."""

    # This status carries no values.
    pass


@dataclass(frozen=True)
class NothingReportStatusIoError:
    """`nothing.report_status` result carried by `task_io_error` (0x23)."""

    # This status carries no values.
    pass


class _NothingReportStatus(TaskBinding):
    """complete with a chosen status and no result

    Schema path `nothing.report_status`, uid 156.

    Returns one of:
      - `NothingReportStatusTimeout` on `task_timeout` (0x22)
      - `NothingReportStatusIoError` on `task_io_error` (0x23)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.NOTHING_REPORT_STATUS
    PATH = "nothing.report_status"
    PARAMS = ("uint8",)
    SHAPES = build_shapes([
        (0x22, NothingReportStatusTimeout, ()),
        (0x23, NothingReportStatusIoError, ()),
    ])

    Timeout = NothingReportStatusTimeout
    IoError = NothingReportStatusIoError

    async def __call__(self, *, code: int) -> NothingReportStatusTimeout | NothingReportStatusIoError | UndeclaredResult:
        """Starts `nothing.report_status` and waits for its reply.

        Args:
            code: `uint8`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([code])


@dataclass(frozen=True)
class ScalarsUnsignedWidthsFinished:
    """`scalars.unsigned_widths` result carried by `finished` (0x20)."""

    u8: int
    u16: int
    u32: int
    u64: int


class _ScalarsUnsignedWidths(TaskBinding):
    """uint8/16/32/64 in one shape, ascending

    Schema path `scalars.unsigned_widths`, uid 230.

    Returns one of:
      - `ScalarsUnsignedWidthsFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.SCALARS_UNSIGNED_WIDTHS
    PATH = "scalars.unsigned_widths"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, ScalarsUnsignedWidthsFinished, ("uint8", "uint16", "uint32", "uint64")),
    ])

    Finished = ScalarsUnsignedWidthsFinished

    async def __call__(self) -> ScalarsUnsignedWidthsFinished | UndeclaredResult:
        """Starts `scalars.unsigned_widths` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class ScalarsSignedWidthsFinished:
    """`scalars.signed_widths` result carried by `finished` (0x20)."""

    i8: int
    i16: int
    i32: int
    i64: int


class _ScalarsSignedWidths(TaskBinding):
    """int8/16/32/64, all negative

    Schema path `scalars.signed_widths`, uid 200.

    Returns one of:
      - `ScalarsSignedWidthsFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.SCALARS_SIGNED_WIDTHS
    PATH = "scalars.signed_widths"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, ScalarsSignedWidthsFinished, ("int8", "int16", "int32", "int64")),
    ])

    Finished = ScalarsSignedWidthsFinished

    async def __call__(self) -> ScalarsSignedWidthsFinished | UndeclaredResult:
        """Starts `scalars.signed_widths` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class ScalarsPlainIntFinished:
    """`scalars.plain_int` result carried by `finished` (0x20)."""

    value: int


class _ScalarsPlainInt(TaskBinding):
    """the bare `int` alias, distinct from int32 in the schema

    Schema path `scalars.plain_int`, uid 50.

    Returns one of:
      - `ScalarsPlainIntFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.SCALARS_PLAIN_INT
    PATH = "scalars.plain_int"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, ScalarsPlainIntFinished, ("int",)),
    ])

    Finished = ScalarsPlainIntFinished

    async def __call__(self) -> ScalarsPlainIntFinished | UndeclaredResult:
        """Starts `scalars.plain_int` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class ScalarsRealsFinished:
    """`scalars.reals` result carried by `finished` (0x20)."""

    f32: float
    f64: float


class _ScalarsReals(TaskBinding):
    """float and double, at values that are not round

    Schema path `scalars.reals`, uid 252.

    Returns one of:
      - `ScalarsRealsFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.SCALARS_REALS
    PATH = "scalars.reals"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, ScalarsRealsFinished, ("float", "double")),
    ])

    Finished = ScalarsRealsFinished

    async def __call__(self) -> ScalarsRealsFinished | UndeclaredResult:
        """Starts `scalars.reals` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class ScalarsFlagsFinished:
    """`scalars.flags` result carried by `finished` (0x20)."""

    yes: bool
    no: bool


class _ScalarsFlags(TaskBinding):
    """bool, both ways

    Schema path `scalars.flags`, uid 235.

    Returns one of:
      - `ScalarsFlagsFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.SCALARS_FLAGS
    PATH = "scalars.flags"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, ScalarsFlagsFinished, ("bool", "bool")),
    ])

    Finished = ScalarsFlagsFinished

    async def __call__(self) -> ScalarsFlagsFinished | UndeclaredResult:
        """Starts `scalars.flags` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class ScalarsPositionalFinished:
    """`scalars.positional` result carried by `finished` (0x20)."""

    v0: int
    v1: int
    v2: int
    v3: float
    v4: bool


class _ScalarsPositional(TaskBinding):
    """the same values again, declared positionally

    Schema path `scalars.positional`, uid 94.

    Returns one of:
      - `ScalarsPositionalFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.SCALARS_POSITIONAL
    PATH = "scalars.positional"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, ScalarsPositionalFinished, ("uint8", "int16", "uint32", "double", "bool")),
    ])

    Finished = ScalarsPositionalFinished

    async def __call__(self) -> ScalarsPositionalFinished | UndeclaredResult:
        """Starts `scalars.positional` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class WideTelemetryFinished:
    """`wide.telemetry` result carried by `finished` (0x20)."""

    d0: float
    d1: float
    d2: float
    d3: float
    d4: float
    d5: float
    d6: float
    d7: float
    d8: float
    d9: float
    d10: float
    d11: float
    d12: float
    d13: float


class _WideTelemetry(TaskBinding):
    """the project's widest result

    Schema path `wide.telemetry`, uid 0.

    Returns one of:
      - `WideTelemetryFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.WIDE_TELEMETRY
    PATH = "wide.telemetry"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, WideTelemetryFinished, ("double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double", "double")),
    ])

    Finished = WideTelemetryFinished

    async def __call__(self) -> WideTelemetryFinished | UndeclaredResult:
        """Starts `wide.telemetry` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class KeyedMeasureFinished:
    """`keyed.measure` result carried by `finished` (0x20)."""

    value: float
    variance: float
    samples: int


@dataclass(frozen=True)
class KeyedMeasureTimeout:
    """`keyed.measure` result carried by `task_timeout` (0x22)."""

    # This status carries no values.
    pass


@dataclass(frozen=True)
class KeyedMeasureIoError:
    """`keyed.measure` result carried by `task_io_error` (0x23)."""

    bus: int


class _KeyedMeasure(TaskBinding):
    """three branches, from eighteen bytes down to zero

    Schema path `keyed.measure`, uid 113.

    Returns one of:
      - `KeyedMeasureFinished` on `finished` (0x20)
      - `KeyedMeasureTimeout` on `task_timeout` (0x22)
      - `KeyedMeasureIoError` on `task_io_error` (0x23)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.KEYED_MEASURE
    PATH = "keyed.measure"
    PARAMS = ("uint8",)
    SHAPES = build_shapes([
        (0x20, KeyedMeasureFinished, ("double", "double", "uint16")),
        (0x22, KeyedMeasureTimeout, ()),
        (0x23, KeyedMeasureIoError, ("uint8",)),
    ])

    Finished = KeyedMeasureFinished
    Timeout = KeyedMeasureTimeout
    IoError = KeyedMeasureIoError

    async def __call__(self, *, branch: int) -> KeyedMeasureFinished | KeyedMeasureTimeout | KeyedMeasureIoError | UndeclaredResult:
        """Starts `keyed.measure` and waits for its reply.

        Args:
            branch: `uint8`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([branch])


@dataclass(frozen=True)
class KeyedConvergeFinished:
    """`keyed.converge` result carried by `finished` (0x20)."""

    iterations: int


@dataclass(frozen=True)
class KeyedConvergeAborted:
    """`keyed.converge` result carried by `aborted` (0x21)."""

    last: int
    iterations: int
    settled: bool


class _KeyedConverge(TaskBinding):
    """the aborted branch, reachable only by force-completing

    Schema path `keyed.converge`, uid 253.

    Returns one of:
      - `KeyedConvergeFinished` on `finished` (0x20)
      - `KeyedConvergeAborted` on `aborted` (0x21)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.KEYED_CONVERGE
    PATH = "keyed.converge"
    PARAMS = ("int32",)
    SHAPES = build_shapes([
        (0x20, KeyedConvergeFinished, ("uint32",)),
        (0x21, KeyedConvergeAborted, ("int32", "uint32", "bool")),
    ])

    Finished = KeyedConvergeFinished
    Aborted = KeyedConvergeAborted

    async def __call__(self, *, target: int) -> KeyedConvergeFinished | KeyedConvergeAborted | UndeclaredResult:
        """Starts `keyed.converge` and waits for its reply.

        Args:
            target: `int32`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([target])


@dataclass(frozen=True)
class KeyedClassifyFinished:
    """`keyed.classify` result carried by `finished` (0x20)."""

    label: int


@dataclass(frozen=True)
class KeyedClassifyCustom71:
    """`keyed.classify` result carried by `custom(0x71)` (0x71)."""

    label: int
    confidence: float
    detail: int


class _KeyedClassify(TaskBinding):
    """a custom status code keying its own shape

    Schema path `keyed.classify`, uid 192.

    Returns one of:
      - `KeyedClassifyFinished` on `finished` (0x20)
      - `KeyedClassifyCustom71` on `custom(0x71)` (0x71)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.KEYED_CLASSIFY
    PATH = "keyed.classify"
    PARAMS = ("uint8",)
    SHAPES = build_shapes([
        (0x20, KeyedClassifyFinished, ("uint8",)),
        (0x71, KeyedClassifyCustom71, ("uint8", "float", "int64")),
    ])

    Finished = KeyedClassifyFinished
    Custom71 = KeyedClassifyCustom71

    async def __call__(self, *, branch: int) -> KeyedClassifyFinished | KeyedClassifyCustom71 | UndeclaredResult:
        """Starts `keyed.classify` and waits for its reply.

        Args:
            branch: `uint8`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([branch])


class _KeyedScope(Scope):
    """status-keyed returns whose branches differ in width

    Schema scope `keyed`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.measure = _KeyedMeasure(client)
        self.converge = _KeyedConverge(client)
        self.classify = _KeyedClassify(client)


class _WideScope(Scope):
    """the shape that sizes the reply frame

    Schema scope `wide`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.telemetry = _WideTelemetry(client)


class _ScalarsScope(Scope):
    """one task per scalar type in TypeMap

    Schema scope `scalars`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.unsigned_widths = _ScalarsUnsignedWidths(client)
        self.signed_widths = _ScalarsSignedWidths(client)
        self.plain_int = _ScalarsPlainInt(client)
        self.reals = _ScalarsReals(client)
        self.flags = _ScalarsFlags(client)
        self.positional = _ScalarsPositional(client)


class _NothingScope(Scope):
    """tasks that answer with a status and no bytes

    Schema scope `nothing`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.acknowledge = _NothingAcknowledge(client)
        self.report_status = _NothingReportStatus(client)


class Tasks(Scope):
    """The project's task tree, mirroring the schema's scopes.

    Construct it with a live `Client`; every task below is an
    awaitable call at the same path the schema declares.
    """

    UID_BYTES = UID_BYTES

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.nothing = _NothingScope(client)
        self.scalars = _ScalarsScope(client)
        self.wide = _WideScope(client)
        self.keyed = _KeyedScope(client)
