import asyncio
from typing import Optional


class FakeStreamReader:
    """Minimal asyncio StreamReader-like object with feed_data + readexactly."""
    def __init__(self) -> None:
        self._buf = bytearray()
        self._data_evt = asyncio.Event()
        self._closed = False

    def feed_data(self, data: bytes) -> None:
        self._buf.extend(data)
        self._data_evt.set()

    async def readexactly(self, n: int) -> bytes:
        while len(self._buf) < n:
            if self._closed:
                # mimic asyncio.IncompleteReadError behavior if you want, but not needed here
                raise asyncio.IncompleteReadError(partial=bytes(self._buf), expected=n)
            self._data_evt.clear()
            await self._data_evt.wait()
        chunk = bytes(self._buf[:n])
        del self._buf[:n]
        return chunk

    def close(self) -> None:
        self._closed = True
        self._data_evt.set()


class FakeStreamWriter:
    """Minimal asyncio StreamWriter-like object capturing writes."""
    def __init__(self) -> None:
        self.buffer = bytearray()
        self._closed = False

    def write(self, data: bytes) -> None:
        if self._closed:
            raise RuntimeError("writer closed")
        self.buffer.extend(data)

    async def drain(self) -> None:
        pass

    def is_closing(self) -> bool:
        return self._closed

    def close(self) -> None:
        self._closed = True

    async def wait_closed(self) -> None:
        pass

    def get_extra_info(self, name: str, default=None):
        # WiFiInterface asks for 'socket' to set keepalive; return None (ok).
        return None
