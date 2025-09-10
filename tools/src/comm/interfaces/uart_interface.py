# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-
"""
Async UART transport using pyserial-asyncio.

Requires:
    pip install pyserial pyserial-asyncio
"""

from __future__ import annotations
import asyncio
from typing import Optional

try:
    import serial_asyncio  # type: ignore
except Exception as e:  # pragma: no cover
    raise ImportError(
        "pyserial-asyncio is required for UART async interface. "
        "Install with: pip install pyserial pyserial-asyncio"
    ) from e

from .interface import Interface, InterfaceError


class UARTInterface(Interface):
    """
    Persistent async UART transport.

    Args:
        port: e.g. 'COM3', '/dev/ttyUSB0', '/dev/ttyACM0'
        baudrate: UART baud
    """

    def __init__(self, port: str, baudrate: int = 115200) -> None:
        super().__init__()
        self._port = port
        self._baud = int(baudrate)
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()

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
                reader, writer = await serial_asyncio.open_serial_connection(
                    url=self._port,
                    baudrate=self._baud,
                )
                self._reader, self._writer = reader, writer
            except Exception as e:
                self._reader = self._writer = None
                raise InterfaceError(f"UART open failed on {self._port}: {e}") from e

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

    async def _send_bytes(self, data: bytes) -> None:
        if not self.is_open:
            await self.open()
        assert self._writer is not None
        try:
            self._writer.write(data)
            await self._writer.drain()
        except Exception as e:
            await self.close()
            raise InterfaceError(f"UART write failed: {e}") from e

    async def _recv_exact(self, n: int) -> bytes:
        if not self.is_open:
            await self.open()
        assert self._reader is not None
        try:
            data = await self._reader.readexactly(n)
            return data
        except asyncio.IncompleteReadError as e:
            await self.close()
            raise InterfaceError(f"UART connection closed (wanted {n}, got {len(e.partial)})") from e
        except Exception as e:
            await self.close()
            raise InterfaceError(f"UART read failed: {e}") from e
