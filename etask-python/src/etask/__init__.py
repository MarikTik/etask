"""etask: the Python side of the etask task framework.

This package is the peer of the C++ ``etask/core`` runtime, in the same way
``ecomm-python`` is the peer of ``ecomm``: every byte layout here is transcribed
from the corresponding C++ header, so a request built in Python decodes on the
device and a reply built on the device decodes here.

It contains only what is *not* project-specific: the status/directive enums, the
flat value codec, the request/reply payload layout, and an async
:class:`~etask.client.Client` that keeps several tasks in flight at once. The
per-task surface -- uids, argument names, result shapes -- is generated from a
project's ``schema.yaml`` by ``python -m schemav2.cli generate --python``, and
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

from etask.client import Client, ClientClosed
from etask.codec import UnknownWireType, pack, unpack, wire_size
from etask.directive import CompletionReason, Directive, Operation, NO_ADDRESSING_ID
from etask.protocol import PayloadTooSmall, Reply, build_request, parse_reply
from etask.status_code import StatusCode, status_name

__all__ = [
    "Client",
    "ClientClosed",
    "CompletionReason",
    "Directive",
    "NO_ADDRESSING_ID",
    "Operation",
    "PayloadTooSmall",
    "Reply",
    "StatusCode",
    "UnknownWireType",
    "build_request",
    "pack",
    "parse_reply",
    "status_name",
    "unpack",
    "wire_size",
]
