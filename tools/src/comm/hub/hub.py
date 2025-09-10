# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-
"""
Hub — fan-out (send) / fan-in (receive) manager over multiple async Interfaces.

- Assumes every interface derives from `comm.interfaces.Interface`.
- Sends run concurrently across all enabled sender interfaces.
- Receives race all enabled receiver interfaces and return the first valid packet.
- No timeouts here; cancellations control lifetime (like other components).
"""

from __future__ import annotations
import asyncio
from typing import Iterable, Optional, Type, Any, List, Set, Tuple

from comm.interfaces.interface import Interface  # your ABC
from comm.protocol import BasicPacket, FramedPacket

Packet = BasicPacket | FramedPacket


class Hub:
    """
    Manage multiple communication interfaces as a single endpoint.

    Responsibilities
    ----------------
    - Lifecycle helpers: `open_all()`, `close_all()`.
    - Enable/disable each interface for sending/receiving at runtime.
    - Send a packet across all enabled senders (concurrently).
    - Try to receive one packet from any enabled receiver (first to complete & validate wins).

    Notes
    -----
    - All interfaces *must* be instances of `Interface` (your ABC). This guarantees
      consistent validator/sealing behavior and unified `try_receive`.
    - `try_receive` simply passes (packet type, size/uid_type, policy) through to each interface's
      `try_receive`. Validation and board filtering are handled inside each interface.
    """

    # ---- construction ------------------------------------------------------

    def __init__(self, interfaces: Iterable[Interface]) -> None:
        """
        Create a hub with a set of interfaces.

        Parameters
        ----------
        interfaces : Iterable[Interface]
            Concrete interface instances (UART, Wi-Fi, etc.). Each must inherit `Interface`.

        All interfaces are initially enabled for both sending and receiving.
        """
        inter_list: List[Interface] = list(interfaces)
        if not inter_list:
            raise ValueError("Hub requires at least one Interface.")
        for iface in inter_list:
            if not isinstance(iface, Interface):
                raise TypeError(f"{iface!r} must inherit comm.interfaces.Interface")

        # Explicitly declared members (no __slots__)
        self._interfaces: Tuple[Interface, ...] = tuple(inter_list)
        self._senders: Set[Interface] = set(self._interfaces)
        self._receivers: Set[Interface] = set(self._interfaces)

    # ---- lifecycle ---------------------------------------------------------

    async def open_all(self) -> None:
        """Open all interfaces concurrently."""
        await asyncio.gather(*(iface.open() for iface in self._interfaces), return_exceptions=False)

    async def close_all(self) -> None:
        """Close all interfaces concurrently (swallows individual close errors)."""
        await asyncio.gather(*(self._safe_close(iface) for iface in self._interfaces), return_exceptions=True)

    async def _safe_close(self, iface: Interface) -> None:
        try:
            await iface.close()
        except Exception:
            # Intentionally ignored: we're trying to close everything best-effort.
            pass

    # Optional convenience for `async with Hub(...)` usage
    async def __aenter__(self) -> "Hub":
        await self.open_all()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close_all()

    # ---- enable/disable routing -------------------------------------------

    def enable_sender(self, iface: Interface) -> None:
        """Allow this interface to be used by `send`."""
        self._require_known(iface)
        self._senders.add(iface)

    def disable_sender(self, iface: Interface) -> None:
        """Disallow this interface from being used by `send`."""
        self._require_known(iface)
        self._senders.discard(iface)

    def enable_receiver(self, iface: Interface) -> None:
        """Allow this interface to be polled by `try_receive`."""
        self._require_known(iface)
        self._receivers.add(iface)

    def disable_receiver(self, iface: Interface) -> None:
        """Disallow this interface from being polled by `try_receive`."""
        self._require_known(iface)
        self._receivers.discard(iface)

    def is_sender_enabled(self, iface: Interface) -> bool:
        """Return True if this interface participates in `send`."""
        self._require_known(iface)
        return iface in self._senders

    def is_receiver_enabled(self, iface: Interface) -> bool:
        """Return True if this interface participates in `try_receive`."""
        self._require_known(iface)
        return iface in self._receivers

    def _require_known(self, iface: Interface) -> None:
        if iface not in self._interfaces:
            raise ValueError("Interface is not managed by this Hub.")

    # ---- high-level operations --------------------------------------------

    async def send(self, packet: Packet) -> None:
        """
        Send `packet` across all enabled sender interfaces concurrently.

        - For `FramedPacket`, sealing (FCS computation) is performed by each interface via its Validator.
        - Errors from individual interfaces will propagate. If you prefer best-effort sends,
          wrap this call and handle exceptions per your application policy.
        """
        tasks = [asyncio.create_task(iface.send(packet)) for iface in self._senders]
        if tasks:
            try:
                await asyncio.gather(*tasks)
            finally:
                # Ensure outstanding tasks are cancelled on error
                for t in tasks:
                    if not t.done():
                        t.cancel()

    async def try_receive(
        self,
        packet_type: Type[Packet],
        **pkt_kwargs: Any,
    ) -> Optional[Packet]:
        """
        Try to receive a packet from any enabled receiver.

        Parameters
        ----------
        packet_type : Type[Packet]
            Either `BasicPacket` or `FramedPacket`.
        **pkt_kwargs :
            Forwarded to each interface's `try_receive(...)`, e.g.:
              - packet_size: int
              - uid_type: ctypes type
              - policy: Checksum (for FramedPacket)

        Returns
        -------
        Optional[Packet]
            The first successfully received & validated packet, or `None`
            if all receivers return `None`. Transport errors from individual
            interfaces are ignored; the race proceeds with others.
        """
        if not self._receivers:
            return None

        tasks = [asyncio.create_task(iface.try_receive(packet_type, **pkt_kwargs)) for iface in self._receivers]
        try:
            for fut in asyncio.as_completed(tasks):
                try:
                    result = await fut
                except Exception:
                    # Ignore a failing receiver; continue the race.
                    continue
                if result is not None:
                    # Cancel other pending tries and return this packet.
                    for t in tasks:
                        if t is not fut and not t.done():
                            t.cancel()
                    # Drain cancellations quietly.
                    await asyncio.gather(*(t for t in tasks if t is not fut), return_exceptions=True)
                    return result
            return None
        finally:
            # Ensure no task is left running.
            for t in tasks:
                if not t.done():
                    t.cancel()
