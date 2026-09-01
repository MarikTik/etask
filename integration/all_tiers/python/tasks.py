"""Generated etask client bindings - do not edit.

Regenerated from the project's schema on every `etask generate --python`
run; 5 task(s).

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

SCHEMA_FINGERPRINT = 0x7ADB9C5658146918
"""The wire contract this client speaks, as eight bytes.

Covers every uid, argument list, result shape and link policy in the
schema this was generated from. The device sends its own at connect; if
the two differ, the peers were built from different schemas and the
client refuses the link rather than trading frames whose uids it would
misread.
"""


class TaskId(IntEnum):
    """Every task's wire uid - the same values as `global::task_id` in C++."""

    INSTANT_PING = 23
    ONESHOT_SAMPLE = 122
    POLLED_COUNT_TO = 71
    POLLED_NEVER_ENDS = 35
    STATEFUL_RESUMABLE = 173




class _InstantPing(InstantTaskBinding):
    """run on arrival and record it

    Schema path `instant.ping`, uid 23.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.INSTANT_PING
    PATH = "instant.ping"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `instant.ping` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class OneshotSampleFinished:
    """`oneshot.sample` result carried by `finished` (0x20)."""

    hooks: int
    executions: int
    reason: int


class _OneshotSample(TaskBinding):
    """one execution step, then answer

    Schema path `oneshot.sample`, uid 122.

    Returns one of:
      - `OneshotSampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ONESHOT_SAMPLE
    PATH = "oneshot.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, OneshotSampleFinished, ("uint8", "uint8", "uint8")),
    ])

    Finished = OneshotSampleFinished

    async def __call__(self) -> OneshotSampleFinished | UndeclaredResult:
        """Starts `oneshot.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class PolledCountToFinished:
    """`polled.count_to` result carried by `finished` (0x20)."""

    hooks: int
    executions: int
    reason: int


class _PolledCountTo(TaskBinding):
    """execute for a fixed number of ticks, then finish

    Schema path `polled.count_to`, uid 71.

    Returns one of:
      - `PolledCountToFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.POLLED_COUNT_TO
    PATH = "polled.count_to"
    PARAMS = ("uint8",)
    SHAPES = build_shapes([
        (0x20, PolledCountToFinished, ("uint8", "uint8", "uint8")),
    ])

    Finished = PolledCountToFinished

    async def __call__(self, *, ticks: int) -> PolledCountToFinished | UndeclaredResult:
        """Starts `polled.count_to` and waits for its reply.

        Args:
            ticks: `uint8`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([ticks])


@dataclass(frozen=True)
class PolledNeverEndsAborted:
    """`polled.never_ends` result carried by `aborted` (0x21)."""

    hooks: int
    executions: int
    reason: int


@dataclass(frozen=True)
class PolledNeverEndsCompletedEarly:
    """`polled.never_ends` result carried by `task_completed_early` (0x28)."""

    hooks: int
    executions: int
    reason: int


class _PolledNeverEnds(TaskBinding):
    """never finishes on its own; only a directive ends it

    Schema path `polled.never_ends`, uid 35.

    Returns one of:
      - `PolledNeverEndsAborted` on `aborted` (0x21)
      - `PolledNeverEndsCompletedEarly` on `task_completed_early` (0x28)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.POLLED_NEVER_ENDS
    PATH = "polled.never_ends"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x21, PolledNeverEndsAborted, ("uint8", "uint8", "uint8")),
        (0x28, PolledNeverEndsCompletedEarly, ("uint8", "uint8", "uint8")),
    ])

    Aborted = PolledNeverEndsAborted
    CompletedEarly = PolledNeverEndsCompletedEarly

    async def __call__(self) -> PolledNeverEndsAborted | PolledNeverEndsCompletedEarly | UndeclaredResult:
        """Starts `polled.never_ends` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class StatefulResumableFinished:
    """`stateful.resumable` result carried by `finished` (0x20)."""

    hooks: int
    executions: int
    executions_at_pause: int
    pauses: int
    resumes: int
    reason: int


@dataclass(frozen=True)
class StatefulResumableCompletedEarly:
    """`stateful.resumable` result carried by `task_completed_early` (0x28)."""

    hooks: int
    executions: int
    executions_at_pause: int
    pauses: int
    resumes: int
    reason: int


class _StatefulResumable(TaskBinding):
    """a long task that pauses and resumes safely

    Schema path `stateful.resumable`, uid 173.

    Returns one of:
      - `StatefulResumableFinished` on `finished` (0x20)
      - `StatefulResumableCompletedEarly` on `task_completed_early` (0x28)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.STATEFUL_RESUMABLE
    PATH = "stateful.resumable"
    PARAMS = ("uint8",)
    SHAPES = build_shapes([
        (0x20, StatefulResumableFinished, ("uint8", "uint8", "uint8", "uint8", "uint8", "uint8")),
        (0x28, StatefulResumableCompletedEarly, ("uint8", "uint8", "uint8", "uint8", "uint8", "uint8")),
    ])

    Finished = StatefulResumableFinished
    CompletedEarly = StatefulResumableCompletedEarly

    async def __call__(self, *, run_for: int) -> StatefulResumableFinished | StatefulResumableCompletedEarly | UndeclaredResult:
        """Starts `stateful.resumable` and waits for its reply.

        Args:
            run_for: `uint8`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([run_for])


class _StatefulScope(Scope):
    """the suspendable tier

    Schema scope `stateful`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.resumable = _StatefulResumable(client)


class _PolledScope(Scope):
    """the runs-across-ticks tier

    Schema scope `polled`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.count_to = _PolledCountTo(client)
        self.never_ends = _PolledNeverEnds(client)


class _OneshotScope(Scope):
    """the run-once-and-answer tier

    Schema scope `oneshot`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _OneshotSample(client)


class _InstantScope(Scope):
    """the fire-and-forget tier

    Schema scope `instant`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.ping = _InstantPing(client)


class Tasks(Scope):
    """The project's task tree, mirroring the schema's scopes.

    Construct it with a live `Client`; every task below is an
    awaitable call at the same path the schema declares.
    """

    UID_BYTES = UID_BYTES

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.instant = _InstantScope(client)
        self.oneshot = _OneshotScope(client)
        self.polled = _PolledScope(client)
        self.stateful = _StatefulScope(client)
