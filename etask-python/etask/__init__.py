"""etask: the Python side of the etask task framework.

This package is the peer of the C++ ``etask/core`` runtime, in the same way
``ecomm-python`` is the peer of ``ecomm``: every byte layout here is transcribed
from the corresponding C++ header, so a request built in Python decodes on the
device and a reply built on the device decodes here.

It contains only what is *not* project-specific: the status/directive enums, the
flat value codec, the request/reply payload layout, and an async
:class:`~etask.client.Client` that keeps several tasks in flight at once. The
per-task surface -- uids, argument names, result shapes -- is generated from a
project's ``schema.yaml`` by ``python -m etask.schema.cli generate --python``, and
imports what it needs from here.

Typical usage::

    import asyncio
    from ecomm.protocol import PacketSchema, Topology, SequencePolicy, ChecksumPolicy
    from ecomm.channels import AsyncTcpChannel
    from etask import Client

    from quadcopter_client import Tasks           # generated from schema.yaml

    async def main():
        schema = PacketSchema(packet_size=32, topology=Topology.NETWORK,
                              sequence=SequencePolicy.NO_SEQUENCE,
                              checksum=ChecksumPolicy.NONE, board_id=2)
        async with AsyncTcpChannel(schema, host="192.168.1.50", port=5000) as channel:
            async with Client(channel, uid_bytes=Tasks.UID_BYTES, receiver_id=1) as client:
                tasks = Tasks(client)
                fix = await tasks.sensors.gps.fix(timeout_ms=5000)
                match fix:
                    case tasks.sensors.gps.fix.Finished(lat=lat, lon=lon):
                        print(lat, lon)

    asyncio.run(main())
"""

# Imported lazily, not eagerly. The client half of this package speaks the wire
# and needs `ecomm`; the code generator (`etask.schema`) needs neither, and is
# run by build systems - CMake, PlatformIO - on machines that are compiling
# firmware, not talking to it. An eager import here would make every one of those
# builds require the whole client dependency chain to emit a header.
#
# PEP 562 module __getattr__ keeps the public surface identical: `from etask
# import Client` works exactly as before, and pays for `ecomm` only then.
_LAZY = {
    "Client": "etask.client",
    "ClientClosed": "etask.client",
    "UnknownWireType": "etask.codec",
    "pack": "etask.codec",
    "unpack": "etask.codec",
    "wire_size": "etask.codec",
    "CompletionReason": "etask.directive",
    "Directive": "etask.directive",
    "Operation": "etask.directive",
    "NO_ADDRESSING_ID": "etask.directive",
    "PayloadTooSmall": "etask.protocol",
    "Reply": "etask.protocol",
    "build_request": "etask.protocol",
    "parse_reply": "etask.protocol",
    "StatusCode": "etask.status_code",
    "status_name": "etask.status_code",
}

__all__ = sorted(_LAZY)


def __getattr__(name):
    """Resolves a public name to its module on first use (PEP 562)."""
    module_name = _LAZY.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import importlib
    value = getattr(importlib.import_module(module_name), name)
    globals()[name] = value          # subsequent lookups skip this path entirely
    return value


def __dir__():
    """Includes the lazily-bound names, so tab completion still shows them."""
    return sorted(set(globals()) | set(_LAZY))
