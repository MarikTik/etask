"""``Client`` -- the async half of etask on a PC.

A device runs many tasks at once; a client that could only do one thing at a
time would throw that away. So launching a task never blocks: it returns an
awaitable that completes whenever *that* task's reply arrives, and a single
background reader dispatches replies as they land::

    async with Client(channel, uid_bytes=1) as client:
        fix, alt = await asyncio.gather(       # both in flight together
            client.launch(GPS_FIX, args=...),
            client.launch(BARO_READ, args=...),
        )

## What the wire can and cannot tell you

A reply is ``[uid][status][result…]`` -- there is **no invocation id**. Two
consequences, both handled here explicitly rather than papered over:

- Replies are matched to launches **FIFO per uid**. With ``concurrency: 1`` (the
  default) that is exact: only one instance of a uid runs at a time. With
  ``concurrency: N`` there may be several instances alive, and nothing on the
  wire says which one finished -- the oldest outstanding launch is resolved.
- ``pause``/``resume``/``complete`` **succeed silently**. The firmware replies to
  those only when they fail (see ``external_channel::dispatch``), so there is no
  acknowledgement to await. They are fire-and-forget here, and a failure surfaces
  as a manager-range reply, routed to :meth:`on_error` (or to the outstanding
  launch for that uid, if there is one).

The rule the reader uses to tell those apart is the status range: a
manager/API code (``< 0x20``) means the manager refused a request and no task
ran; a task-range code means a task actually completed.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from collections.abc import Awaitable
from typing import Callable, Deque, Dict, Optional

import warnings

from etask.directive import CompletionReason, Operation
from etask.preamble import SIZE as _PREAMBLE_SIZE
from etask.preamble import PreambleError, SchemaMismatch, decode as _decode_preamble
from etask.preamble import discardable as _discardable, encode as _encode_preamble, find as _find_preamble
from etask.protocol import Reply, build_request, parse_reply


class ClientClosed(RuntimeError):
    """Raised when a launch is attempted on a client that is shutting down."""


async def _maybe_await(value):
    """Awaits `value` if the transport's method was a coroutine.

    A raw byte path may reasonably be sync (pyserial) or async (asyncio
    streams); accepting both keeps the hook cheap to implement.

    @param value Whatever the transport method returned.
    @return Its result, awaited if necessary.
    """
    if hasattr(value, "__await__"):
        return await value
    return value


class Client:
    """Drives one etask device over an ``ecomm`` async channel.

    Args:
        channel: An ``ecomm.channels.AsyncChannel`` -- typically
            ``AsyncTcpChannel`` over Wi-Fi. Not owned: opening and closing it is
            the caller's business, so one channel can serve several clients.
        uid_bytes: The project's uid width, from its uid ledger.
        receiver_id: Node id to address requests to, under an addressed
            topology. ``None`` leaves the header alone (point-to-point).
        on_error: Called with a :class:`Reply` when the device reports a
            manager-range failure that no outstanding launch claims -- a rejected
            pause, say. Defaults to ignoring it.
        on_orphan: Called with a :class:`Reply` for a completion nobody is
            waiting for (a task started from the device itself, or a launch
            already timed out). Defaults to ignoring it.
    """

    def __init__(
        self,
        channel,
        *,
        uid_bytes: int,
        receiver_id: Optional[int] = None,
        fingerprint: Optional[int] = None,
        on_error: Optional[Callable[[Reply], None]] = None,
        on_orphan: Optional[Callable[[Reply], None]] = None,
    ) -> None:
        self._channel = channel
        self._uid_bytes = uid_bytes
        self._receiver_id = receiver_id
        self._fingerprint = fingerprint
        self._on_error = on_error
        self._on_orphan = on_orphan
        self._pending: Dict[int, Deque[asyncio.Future]] = defaultdict(deque)
        self._reader: Optional[asyncio.Task] = None
        self._closing = False
        #: Bytes read past the handshake preamble that the transport could not
        #: take back. Empty unless a transport lacks `unread_raw`.
        self._pending_raw: bytes = b""

    # ------------------------------------------------------------- lifecycle

    async def __aenter__(self) -> "Client":
        await self.handshake()
        self.start()
        return self

    async def handshake(self, timeout: float = 2.0) -> bool:
        """Exchanges schema fingerprints with the device, before any traffic.

        Two peers generated from different schemas may agree on every byte of
        frame layout and none of the meaning: the frames parse, the checksum
        passes, and the device runs the wrong task with plausible arguments.
        The fingerprint catches that, and it is exchanged in a fixed preamble
        rather than a packet because two ends that disagree about a header
        cannot use a normal frame to say so.

        Skipped, with a warning, when this client was given no ``fingerprint``
        or when the transport exposes no raw byte path - the same opt-in shape
        the device side has, so an older transport keeps working rather than
        breaking on upgrade.

        @param timeout Seconds to wait for the device's preamble.
        @return True if the contracts were compared and matched; False if the
                handshake was skipped.
        @throws SchemaMismatch If the device speaks a different contract, or
                sent something that was not a preamble.
        """
        if self._fingerprint is None:
            return False

        send_raw = getattr(self._channel, "send_raw", None)
        read_raw = getattr(self._channel, "read_raw", None)
        if send_raw is None or read_raw is None:
            warnings.warn(
                "schema handshake skipped: this transport has no send_raw/read_raw, "
                "so the 14-byte preamble cannot be exchanged. A schema mismatch will "
                "surface as unanswered requests rather than a clear error.",
                RuntimeWarning,
                stacklevel=2,
            )
            return False

        # Both peers send immediately rather than waiting to be spoken to:
        # symmetric, one round trip, and neither side can hang waiting to start.
        await _maybe_await(send_raw(_encode_preamble(self._fingerprint)))

        buffer = bytearray()
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while True:
            at = _find_preamble(bytes(buffer))
            if at >= 0:
                error, peer = _decode_preamble(bytes(buffer[at:at + _PREAMBLE_SIZE]), self._fingerprint)
                if error is not PreambleError.NONE:
                    raise SchemaMismatch(error, self._fingerprint, peer)
                # Anything past the preamble is task traffic that this read
                # happened to pull in. Hand it back rather than dropping it:
                # on a stream transport those bytes are the start of a frame
                # and there is nobody else to recover them.
                leftover = bytes(buffer[at + _PREAMBLE_SIZE:])
                if leftover:
                    pushback = getattr(self._channel, "unread_raw", None)
                    if pushback is not None:
                        await _maybe_await(pushback(leftover))
                    else:
                        self._pending_raw = leftover
                return True

            # Drop what cannot begin a preamble, so a silent peer cannot grow
            # this buffer without bound while we wait.
            del buffer[:_discardable(bytes(buffer))]

            remaining = deadline - loop.time()
            if remaining <= 0:
                raise SchemaMismatch(PreambleError.BAD_MAGIC, self._fingerprint, None)

            chunk = await _maybe_await(read_raw(64))
            if chunk:
                buffer.extend(chunk)
            else:
                await asyncio.sleep(0.01)

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    def start(self) -> None:
        """Starts the background reader. Idempotent."""
        if self._reader is None:
            self._closing = False
            self._reader = asyncio.create_task(self._read_loop(), name="etask-client-reader")

    async def aclose(self) -> None:
        """Stops the reader and fails every launch still waiting."""
        self._closing = True
        if self._reader is not None:
            self._reader.cancel()
            try:
                await self._reader
            except asyncio.CancelledError:
                pass
            self._reader = None
        self._fail_all(ClientClosed("client closed while the reply was outstanding"))

    # ---------------------------------------------------------------- sending

    def launch(self, uid: int, args: bytes = b"") -> "asyncio.Future[Reply]":
        """Starts a task and returns the awaitable for its reply.

        The send happens immediately; the returned future resolves when the
        device replies -- either a completion, or a manager-range rejection if
        the task could not be started at all.
        """
        if self._closing:
            raise ClientClosed("client is closed")
        future: "asyncio.Future[Reply]" = asyncio.get_running_loop().create_future()
        self._pending[uid].append(future)
        # A caller that gives up (asyncio.wait_for, an explicit cancel) must not
        # leave its slot in the queue: the next reply would resolve a dead future
        # and every later launch of this uid would be matched one reply late.
        future.add_done_callback(lambda done: self._discard(uid, done))
        try:
            self._send(uid, Operation.REGISTER_TASK, args=args)
        except BaseException:
            self._discard(uid, future)
            raise
        return future

    def _discard(self, uid: int, future: "asyncio.Future[Reply]") -> None:
        """Drops a future from the pending queue if it is still sitting there."""
        queue = self._pending.get(uid)
        if not queue:
            return
        try:
            queue.remove(future)
        except ValueError:
            pass  # already resolved and popped by the reader

    def dispatch(self, uid: int, args: bytes = b"") -> None:
        """Runs a fire-and-forget command, with nothing to wait for.

        The counterpart to :meth:`launch` for an ``instant_task``: the device
        runs the command inside the call that receives it and sends **no reply**,
        so there is no future to resolve and nothing to await. The send itself is
        immediate.

        Because nothing comes back, a command that the device rejects - an
        unknown uid, a payload it cannot unpack - fails silently here. That is
        the tier's contract, not a gap: a task whose outcome the caller needs to
        know is a ``oneshot_task``, and reaches this client through
        :meth:`launch`.
        """
        if self._closing:
            raise ClientClosed("client is closed")
        self._send(uid, Operation.REGISTER_TASK, args=args)

    def pause(self, uid: int) -> None:
        """Asks the device to pause a task. Succeeds silently (see the module doc)."""
        self._send(uid, Operation.PAUSE_TASK)

    def resume(self, uid: int) -> None:
        """Asks the device to resume a paused task. Succeeds silently."""
        self._send(uid, Operation.RESUME_TASK)

    def complete(self, uid: int, reason: int = CompletionReason.ABORTED) -> None:
        """Force-completes a task.

        The task's ``on_complete`` still runs, so this *does* produce a reply --
        which resolves the outstanding launch for that uid, exactly as a natural
        completion would.
        """
        self._send(uid, Operation.COMPLETE_TASK, reason=int(reason))

    def _send(self, uid: int, operation: Operation, *, reason: int = 0, args: bytes = b"") -> None:
        packet = build_request(
            self._channel.schema,
            uid=uid,
            uid_bytes=self._uid_bytes,
            operation=operation,
            reason=reason,
            args=args,
            receiver_id=self._receiver_id,
        )
        result = self._channel.send(packet)
        if isinstance(result, Awaitable):
            # An async channel returns a coroutine; let it run without making
            # every caller await a send that cannot meaningfully fail here.
            asyncio.ensure_future(result)

    # -------------------------------------------------------------- receiving

    async def _read_loop(self) -> None:
        while True:
            packet = await self._channel.receive()
            if packet is None:
                continue
            self._dispatch(parse_reply(packet, uid_bytes=self._uid_bytes))

    def _dispatch(self, reply: Reply) -> None:
        queue = self._pending.get(reply.uid)
        if queue:
            future = queue.popleft()
            if not future.done():
                future.set_result(reply)
            return
        if reply.is_rejection:
            if self._on_error is not None:
                self._on_error(reply)
            return
        if self._on_orphan is not None:
            self._on_orphan(reply)

    def _fail_all(self, error: BaseException) -> None:
        for queue in self._pending.values():
            while queue:
                future = queue.popleft()
                if not future.done():
                    future.set_exception(error)
        self._pending.clear()
