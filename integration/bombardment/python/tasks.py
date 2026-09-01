"""Generated etask client bindings - do not edit.

Regenerated from the project's schema on every `etask generate --python`
run; 6 task(s).

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

SCHEMA_FINGERPRINT = 0xFA26FB9CB887FDEA
"""The wire contract this client speaks, as eight bytes.

Covers every uid, argument list, result shape and link policy in the
schema this was generated from. The device sends its own at connect; if
the two differ, the peers were built from different schemas and the
client refuses the link rather than trading frames whose uids it would
misread.
"""


class TaskId(IntEnum):
    """Every task's wire uid - the same values as `global::task_id` in C++."""

    SWARM_SALVO = 3
    SWARM_VOLLEY = 5
    SWARM_SINGLE = 4
    SWARM_PROBE = 2
    HOLD_LATCH = 0
    RESET_COUNTERS = 1




@dataclass(frozen=True)
class SwarmSalvoFinished:
    """`swarm.salvo` result carried by `finished` (0x20)."""

    ticks_run: int


class _SwarmSalvo(TaskBinding):
    """occupy a polled record for a fixed number of ticks

    Schema path `swarm.salvo`, uid 3.

    Returns one of:
      - `SwarmSalvoFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.SWARM_SALVO
    PATH = "swarm.salvo"
    PARAMS = ("uint16",)
    SHAPES = build_shapes([
        (0x20, SwarmSalvoFinished, ("uint16",)),
    ])

    Finished = SwarmSalvoFinished

    async def __call__(self, *, ticks: int) -> SwarmSalvoFinished | UndeclaredResult:
        """Starts `swarm.salvo` and waits for its reply.

        Args:
            ticks: `uint16`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([ticks])


@dataclass(frozen=True)
class SwarmVolleyFinished:
    """`swarm.volley` result carried by `finished` (0x20)."""

    ticks_run: int


class _SwarmVolley(TaskBinding):
    """occupy a polled record, but only two at a time

    Schema path `swarm.volley`, uid 5.

    Returns one of:
      - `SwarmVolleyFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.SWARM_VOLLEY
    PATH = "swarm.volley"
    PARAMS = ("uint16",)
    SHAPES = build_shapes([
        (0x20, SwarmVolleyFinished, ("uint16",)),
    ])

    Finished = SwarmVolleyFinished

    async def __call__(self, *, ticks: int) -> SwarmVolleyFinished | UndeclaredResult:
        """Starts `swarm.volley` and waits for its reply.

        Args:
            ticks: `uint16`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([ticks])


@dataclass(frozen=True)
class SwarmSingleFinished:
    """`swarm.single` result carried by `finished` (0x20)."""

    ticks_run: int


class _SwarmSingle(TaskBinding):
    """occupy a polled record, one instance only

    Schema path `swarm.single`, uid 4.

    Returns one of:
      - `SwarmSingleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.SWARM_SINGLE
    PATH = "swarm.single"
    PARAMS = ("uint16",)
    SHAPES = build_shapes([
        (0x20, SwarmSingleFinished, ("uint16",)),
    ])

    Finished = SwarmSingleFinished

    async def __call__(self, *, ticks: int) -> SwarmSingleFinished | UndeclaredResult:
        """Starts `swarm.single` and waits for its reply.

        Args:
            ticks: `uint16`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([ticks])


@dataclass(frozen=True)
class SwarmProbeFinished:
    """`swarm.probe` result carried by `finished` (0x20)."""

    served: bool


class _SwarmProbe(TaskBinding):
    """take a polled record for exactly one tick

    Schema path `swarm.probe`, uid 2.

    Returns one of:
      - `SwarmProbeFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.SWARM_PROBE
    PATH = "swarm.probe"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, SwarmProbeFinished, ("bool",)),
    ])

    Finished = SwarmProbeFinished

    async def __call__(self) -> SwarmProbeFinished | UndeclaredResult:
        """Starts `swarm.probe` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class HoldLatchFinished:
    """`hold.latch` result carried by `finished` (0x20)."""

    ticks_run: int


class _HoldLatch(TaskBinding):
    """hold a stateful record until told otherwise

    Schema path `hold.latch`, uid 0.

    Returns one of:
      - `HoldLatchFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.HOLD_LATCH
    PATH = "hold.latch"
    PARAMS = ("uint16",)
    SHAPES = build_shapes([
        (0x20, HoldLatchFinished, ("uint16",)),
    ])

    Finished = HoldLatchFinished

    async def __call__(self, *, ticks: int) -> HoldLatchFinished | UndeclaredResult:
        """Starts `hold.latch` and waits for its reply.

        Args:
            ticks: `uint16`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([ticks])


class _ResetCounters(InstantTaskBinding):
    """zero the harness's bookkeeping, now

    Schema path `reset_counters`, uid 1.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.RESET_COUNTERS
    PATH = "reset_counters"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `reset_counters` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


class _HoldScope(Scope):
    """the stateful tier - a separate manager with a separate budget

    Schema scope `hold`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.latch = _HoldLatch(client)


class _SwarmScope(Scope):
    """the bombardment surface - tasks that exist only to occupy records

    Schema scope `swarm`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.salvo = _SwarmSalvo(client)
        self.volley = _SwarmVolley(client)
        self.single = _SwarmSingle(client)
        self.probe = _SwarmProbe(client)


class Tasks(Scope):
    """The project's task tree, mirroring the schema's scopes.

    Construct it with a live `Client`; every task below is an
    awaitable call at the same path the schema declares.
    """

    UID_BYTES = UID_BYTES

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.swarm = _SwarmScope(client)
        self.hold = _HoldScope(client)
        self.reset_counters = _ResetCounters(client)
