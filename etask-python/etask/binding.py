"""The base types generated task bindings are built from.

A generated module declares *what* a project's tasks are -- uid, argument types,
and one dataclass per declared result shape. Everything about *how* a call
travels (packing, launching, matching the reply's status byte to a shape, and
decoding it) lives here, so the generated file stays a description rather than a
copy of the runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Sequence, Tuple, Type

from etask.client import Client
from etask.codec import pack, unpack
from etask.directive import CompletionReason
from etask.protocol import Reply
from etask.status_code import status_name


class TaskRejected(RuntimeError):
    """Raised when the device refused to run the task at all.

    The status is a manager/API code (``< 0x20``) -- an unknown uid, a full
    concurrency slot, malformed arguments -- which means ``on_complete`` never
    ran and there is no result to decode. It is an exception rather than a
    returned value precisely because there is no result shape to match on.
    """

    def __init__(self, reply: Reply, task: str):
        super().__init__(
            f"device refused to start '{task}': {reply.status_name} "
            f"(0x{reply.status:02X})"
        )
        self.reply = reply
        self.task = task


@dataclass(frozen=True)
class UndeclaredResult:
    """A completion whose status the schema declares no shape for.

    Legitimate and not an error: a task force-completed from elsewhere replies
    ``task_aborted`` with no values, and a schema need not spell that out. The
    raw bytes are kept so a caller who knows better can still decode them.
    """

    status: int
    raw: bytes

    @property
    def status_name(self) -> str:
        return status_name(self.status)


class TaskBinding:
    """One task, bound to a client. Generated subclasses fill in the class data.

    Subclasses declare:
        UID:    the task's wire id.
        PATH:   its dotted schema path, for error messages.
        PARAMS: the constructor argument types, in wire order.
        SHAPES: ``status code -> (dataclass, value types)``.
    """

    UID: int = 0
    PATH: str = ""
    PARAMS: Tuple[str, ...] = ()
    SHAPES: Mapping[int, Tuple[Type[Any], Tuple[str, ...]]] = {}

    def __init__(self, client: Client) -> None:
        self._client = client

    # ------------------------------------------------------------- invocation

    async def _invoke(self, values: Sequence[Any]) -> Any:
        """Packs the arguments, launches, and decodes whatever comes back."""
        reply = await self._client.launch(self.UID, pack(self.PARAMS, values))
        return self._decode(reply)

    def _decode(self, reply: Reply) -> Any:
        if reply.is_rejection:
            raise TaskRejected(reply, self.PATH)
        shape = self.SHAPES.get(reply.status)
        if shape is None:
            return UndeclaredResult(status=reply.status, raw=reply.result)
        cls, types = shape
        return cls(*unpack(types, reply.result)) if types else cls()

    # --------------------------------------------------------------- controls

    def pause(self) -> None:
        """Pauses the running instance. Succeeds silently (see :mod:`etask.client`)."""
        self._client.pause(self.UID)

    def resume(self) -> None:
        """Resumes the paused instance. Succeeds silently."""
        self._client.resume(self.UID)

    def complete(self, reason: int = CompletionReason.ABORTED) -> None:
        """Force-completes the running instance; its reply resolves the pending call."""
        self._client.complete(self.UID, reason)


class InstantTaskBinding:
    """One fire-and-forget command, bound to a client.

    The counterpart to :class:`TaskBinding` for an ``instant_task``. The device
    runs the command inside the call that delivers it and sends no reply, so
    invoking one is a plain call rather than a coroutine - there is nothing to
    await and nothing to decode.

    It carries no ``pause``/``resume``/``complete`` either. Those address a live
    task, and an instant command is never live: by the time any directive could
    arrive it has already run and been destroyed. The device answers such a
    request with ``status_code.TASK_NOT_ADDRESSABLE``, so offering the methods
    here would only invite a call that cannot work.

    Subclasses declare:
        UID:    the command's wire id.
        PATH:   its dotted schema path, for error messages.
        PARAMS: the constructor argument types, in wire order.
    """

    UID: int = 0
    PATH: str = ""
    PARAMS: Tuple[str, ...] = ()

    def __init__(self, client: Client) -> None:
        self._client = client

    def _dispatch(self, values: Sequence[Any]) -> None:
        """Packs the arguments and sends. Returns as soon as the bytes are away."""
        self._client.dispatch(self.UID, pack(self.PARAMS, values))


class Scope:
    """A branch of the generated task tree -- a schema scope, as an object.

    Holds nothing but its children; it exists so a task's schema path reads the
    same in Python as in the schema (``tasks.sensors.gps.fix``).
    """

    __slots__ = ("_client",)

    def __init__(self, client: Client) -> None:
        self._client = client


def build_shapes(
    entries: Sequence[Tuple[int, Type[Any], Tuple[str, ...]]]
) -> Dict[int, Tuple[Type[Any], Tuple[str, ...]]]:
    """Turns a generated shape list into the lookup table ``_decode`` uses."""
    return {code: (cls, types) for code, cls, types in entries}
