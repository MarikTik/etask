"""Generated etask client bindings - do not edit.

Regenerated from the project's schema on every `etask generate --python`
run; 4 task(s).

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

SCHEMA_FINGERPRINT = 0x53A1848E44D79BF4
"""The wire contract this client speaks, as eight bytes.

Covers every uid, argument list, result shape and link policy in the
schema this was generated from. The device sends its own at connect; if
the two differ, the peers were built from different schemas and the
client refuses the link rather than trading frames whose uids it would
misread.
"""


class TaskId(IntEnum):
    """Every task's wire uid - the same values as `global::task_id` in C++."""

    BULK_TRANSFER = 0
    TELEMETRY_SAMPLE = 3
    SHARED_ECHO = 2
    PING = 1




@dataclass(frozen=True)
class BulkTransferFinished:
    """`bulk.transfer` result carried by `finished` (0x20)."""

    sum: int
    count: int
    first: int
    last: int


class _BulkTransfer(TaskBinding):
    """accept a wide payload and answer with a wide one

    Schema path `bulk.transfer`, uid 0.

    Returns one of:
      - `BulkTransferFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.BULK_TRANSFER
    PATH = "bulk.transfer"
    PARAMS = ("uint32", "uint32", "uint32", "uint32", "uint32", "uint32", "uint32", "uint32")
    SHAPES = build_shapes([
        (0x20, BulkTransferFinished, ("uint64", "uint32", "uint32", "uint32")),
    ])

    Finished = BulkTransferFinished

    async def __call__(self, *, a: int, b: int, c: int, d: int, e: int, f: int, g: int, h: int) -> BulkTransferFinished | UndeclaredResult:
        """Starts `bulk.transfer` and waits for its reply.

        Args:
            a: `uint32`.
            b: `uint32`.
            c: `uint32`.
            d: `uint32`.
            e: `uint32`.
            f: `uint32`.
            g: `uint32`.
            h: `uint32`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([a, b, c, d, e, f, g, h])


@dataclass(frozen=True)
class TelemetrySampleFinished:
    """`telemetry.sample` result carried by `finished` (0x20)."""

    value: int


class _TelemetrySample(TaskBinding):
    """read one counter

    Schema path `telemetry.sample`, uid 3.

    Returns one of:
      - `TelemetrySampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.TELEMETRY_SAMPLE
    PATH = "telemetry.sample"
    PARAMS = ("uint8",)
    SHAPES = build_shapes([
        (0x20, TelemetrySampleFinished, ("uint16",)),
    ])

    Finished = TelemetrySampleFinished

    async def __call__(self, *, channel: int) -> TelemetrySampleFinished | UndeclaredResult:
        """Starts `telemetry.sample` and waits for its reply.

        Args:
            channel: `uint8`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([channel])


@dataclass(frozen=True)
class SharedEchoFinished:
    """`shared.echo` result carried by `finished` (0x20)."""

    token: int
    served: int


class _SharedEcho(TaskBinding):
    """return the argument, and which link asked

    Schema path `shared.echo`, uid 2.

    Returns one of:
      - `SharedEchoFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.SHARED_ECHO
    PATH = "shared.echo"
    PARAMS = ("uint16",)
    SHAPES = build_shapes([
        (0x20, SharedEchoFinished, ("uint16", "uint8")),
    ])

    Finished = SharedEchoFinished

    async def __call__(self, *, token: int) -> SharedEchoFinished | UndeclaredResult:
        """Starts `shared.echo` and waits for its reply.

        Args:
            token: `uint16`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([token])


@dataclass(frozen=True)
class PingFinished:
    """`ping` result carried by `finished` (0x20)."""

    alive: bool


class _Ping(TaskBinding):
    """a root-level task, belonging to no subsystem

    Schema path `ping`, uid 1.

    Returns one of:
      - `PingFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.PING
    PATH = "ping"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, PingFinished, ("bool",)),
    ])

    Finished = PingFinished

    async def __call__(self) -> PingFinished | UndeclaredResult:
        """Starts `ping` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _SharedScope(Scope):
    """carried by both links

    Schema scope `shared`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.echo = _SharedEcho(client)


class _TelemetryScope(Scope):
    """the narrow subsystem, carried by `bench` alone

    Schema scope `telemetry`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _TelemetrySample(client)


class _BulkScope(Scope):
    """the wide subsystem, carried by `net` alone

    Schema scope `bulk`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.transfer = _BulkTransfer(client)


class Tasks(Scope):
    """The project's task tree, mirroring the schema's scopes.

    Construct it with a live `Client`; every task below is an
    awaitable call at the same path the schema declares.
    """

    UID_BYTES = UID_BYTES

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.bulk = _BulkScope(client)
        self.telemetry = _TelemetryScope(client)
        self.shared = _SharedScope(client)
        self.ping = _Ping(client)
