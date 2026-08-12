"""Request and reply payload layout -- mirrors ``protocol/request.hpp`` and
``protocol/reply.hpp``.

An ``ecomm`` packet's payload is a raw byte region; etask defines what goes in
it. Two shapes, both little-endian, both starting at payload offset 0::

    request:  [directive 1B][uid NB][args…]
    reply:    [uid NB][status 1B][result…]

``N`` is the project's uid width, which the schema generator pins in the uid
ledger (``uid_bytes``) and which the generated bindings pass in here. The uid is
raw bytes -- a ``memcpy`` of the enum on the C++ side, not a serialized value --
so it is read and written with the same little-endian width on both ends.
"""

from __future__ import annotations

from dataclasses import dataclass

from ecomm.protocol.header_options import HeaderOptions
from ecomm.protocol.header_type import HeaderType
from ecomm.protocol.packet import Packet
from ecomm.protocol.schema import PacketSchema

from etask.directive import Directive, Operation
from etask.status_code import StatusCode, status_name


class PayloadTooSmall(ValueError):
    """Raised when a packet's payload cannot hold the fields being written."""


def build_request(
    schema: PacketSchema,
    *,
    uid: int,
    uid_bytes: int,
    operation: Operation,
    reason: int = 0,
    args: bytes = b"",
    receiver_id: int | None = None,
) -> Packet:
    """Builds a request packet: directive byte, uid, then the argument bytes.

    Args:
        schema: The packet schema shared with the firmware.
        uid: The target task's wire id.
        uid_bytes: Width of the uid field, from the project's uid ledger.
        operation: Which ``task_manager`` operation to invoke.
        reason: Completion reason, meaningful only for ``COMPLETE_TASK``.
        args: Already-packed constructor arguments (see :mod:`etask.codec`).
        receiver_id: Destination node, for an addressed topology.

    Returns:
        A packet ready to send.
    """
    needed = 1 + uid_bytes + len(args)
    if needed > schema.payload_size:
        raise PayloadTooSmall(
            f"a request for uid {uid} needs {needed} payload byte(s) "
            f"(1 directive + {uid_bytes} uid + {len(args)} args) but the packet "
            f"carries {schema.payload_size}; enlarge packet_size or shrink the task's params"
        )

    packet = Packet(schema, HeaderType.DATA, HeaderOptions.NONE)
    packet.payload[0] = Directive(operation, reason).raw
    packet.payload[1:1 + uid_bytes] = uid.to_bytes(uid_bytes, "little")
    if args:
        packet.payload[1 + uid_bytes:1 + uid_bytes + len(args)] = args
    if receiver_id is not None:
        packet.header.receiver_id = receiver_id
    return packet


@dataclass(frozen=True)
class Reply:
    """A parsed reply payload: which task, how it ended, and its raw result.

    The result bytes are left undecoded here on purpose -- what they mean depends
    on :attr:`status`, and only the generated per-task bindings know the shapes.
    """

    uid: int
    status: int
    result: bytes

    @property
    def status_name(self) -> str:
        return status_name(self.status)

    @property
    def is_rejection(self) -> bool:
        """Whether the manager refused the request outright, so no task ran.

        Manager-range codes are returned by ``task_manager`` itself (unknown uid,
        concurrency cap reached, ...) and carry no result bytes.
        """
        return self.status < 0x20

    @property
    def is_finished(self) -> bool:
        return self.status == StatusCode.TASK_FINISHED


def parse_reply(packet: Packet, *, uid_bytes: int) -> Reply:
    """Reads a reply packet's payload into named fields."""
    if packet.schema.payload_size < uid_bytes + 1:
        raise PayloadTooSmall(
            f"a reply needs {uid_bytes + 1} payload byte(s) but the packet carries "
            f"{packet.schema.payload_size}"
        )
    payload = bytes(packet.payload)
    uid = int.from_bytes(payload[0:uid_bytes], "little")
    status = payload[uid_bytes]
    return Reply(uid=uid, status=status, result=payload[uid_bytes + 1:])
