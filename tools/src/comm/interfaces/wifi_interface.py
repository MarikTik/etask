# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-
"""
Async TCP (Wi-Fi) transport using asyncio streams.
"""

from __future__ import annotations
import asyncio
import socket
from typing import Optional

from .interface import Interface, InterfaceError


class WiFiInterface(Interface):
    """
    Persistent TCP client using asyncio streams.

    Args:
        host: device IP/hostname
        port: TCP port
        keepalive: enable SO_KEEPALIVE on the underlying socket
    """

    def __init__(self, host: str, port: int, *, keepalive: bool = True) -> None:
        super().__init__()
        self._host = host
        self._port = int(port)
        self._keepalive = bool(keepalive)
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()  # serialize connect/reconnect

    # -- lifecycle --

    @property
    def is_open(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    async def open(self) -> None:
        if self.is_open:
            return
        async with self._lock:
            if self.is_open:
                return
            try:
                reader, writer = await asyncio.open_connection(self._host, self._port)
                if self._keepalive:
                    sock = writer.get_extra_info("socket")
                    if isinstance(sock, socket.socket):
                        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                self._reader, self._writer = reader, writer
            except Exception as e:
                self._reader = self._writer = None
                raise InterfaceError(f"TCP connect to {self._host}:{self._port} failed: {e}") from e

    async def close(self) -> None:
        async with self._lock:
            try:
                if self._writer:
                    self._writer.close()
                    try:
                        await self._writer.wait_closed()
                    except Exception:
                        pass
            finally:
                self._reader = self._writer = None

    # -- raw I/O --

    async def _send_bytes(self, data: bytes) -> None:
        if not self.is_open:
            await self.open()
        assert self._writer is not None
        try:
            self._writer.write(data)
            await self._writer.drain()
        except Exception as e:
            await self.close()
            raise InterfaceError(f"TCP send failed: {e}") from e

    async def _recv_exact(self, n: int) -> bytes:
        if not self.is_open:
            await self.open()
        assert self._reader is not None
        try:
            data = await self._reader.readexactly(n)
            return data
        except asyncio.IncompleteReadError as e:
            await self.close()
            raise InterfaceError(f"TCP connection closed (wanted {n}, got {len(e.partial)})") from e
        except Exception as e:
            await self.close()
            raise InterfaceError(f"TCP recv failed: {e}") from e
