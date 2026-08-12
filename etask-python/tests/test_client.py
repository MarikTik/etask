# etask-python/tests/test_client.py
# SPDX-License-Identifier: MIT
"""The async client: many tasks in flight, replies matched as they arrive.

Driven with ``asyncio.run`` rather than pytest-asyncio so the suite needs no
plugin.
"""

import asyncio

import pytest
from ecomm.protocol.header_options import HeaderOptions
from ecomm.protocol.header_type import HeaderType
from ecomm.protocol.packet import Packet
from ecomm.protocol.schema import PacketSchema
from ecomm.protocol.topology import Topology

from etask.client import Client, ClientClosed
from etask.directive import Directive, Operation
from etask.status_code import StatusCode

SCHEMA = PacketSchema(packet_size=32, topology=Topology.NETWORK, board_id=2)
UID_BYTES = 1


class FakeChannel:
    """An AsyncChannel stand-in: records sends, replays queued replies."""

    def __init__(self):
        self.schema = SCHEMA
        self.sent = []
        self._inbox = asyncio.Queue()

    async def send(self, packet):
        self.sent.append(packet)
        return 0

    async def receive(self):
        return await self._inbox.get()

    def deliver(self, uid: int, status: int, result: bytes = b""):
        packet = Packet(self.schema, HeaderType.DATA, HeaderOptions.NONE)
        packet.payload[0:UID_BYTES] = uid.to_bytes(UID_BYTES, "little")
        packet.payload[UID_BYTES] = status
        if result:
            packet.payload[UID_BYTES + 1:UID_BYTES + 1 + len(result)] = result
        self._inbox.put_nowait(packet)


def run(coro):
    return asyncio.run(coro)


async def settle():
    """Lets the reader task run to a quiescent point."""
    for _ in range(4):
        await asyncio.sleep(0)


# -----------------------
# Launching
# -----------------------

def test_launch_sends_a_register_request():
    async def scenario():
        channel = FakeChannel()
        async with Client(channel, uid_bytes=UID_BYTES, receiver_id=1) as client:
            client.launch(7, args=b"\x01\x02")
            await settle()
        return channel.sent

    sent = run(scenario())
    assert len(sent) == 1
    assert Directive.unpack(sent[0].payload[0]).command is Operation.REGISTER_TASK
    assert sent[0].payload[1] == 7
    assert bytes(sent[0].payload[2:4]) == b"\x01\x02"
    assert sent[0].header.receiver_id == 1


def test_launch_resolves_when_its_reply_arrives():
    async def scenario():
        channel = FakeChannel()
        async with Client(channel, uid_bytes=UID_BYTES) as client:
            pending = client.launch(7)
            channel.deliver(7, StatusCode.TASK_FINISHED, b"\x2a")
            return await asyncio.wait_for(pending, 1.0)

    reply = run(scenario())
    assert reply.uid == 7 and reply.is_finished and reply.result[0] == 0x2A


def test_several_tasks_are_in_flight_at_once():
    # The point of the async client: launching does not serialize on completion,
    # and replies may come back in any order.
    async def scenario():
        channel = FakeChannel()
        async with Client(channel, uid_bytes=UID_BYTES) as client:
            a, b, c = client.launch(1), client.launch(2), client.launch(3)
            channel.deliver(3, StatusCode.TASK_FINISHED)
            channel.deliver(1, StatusCode.TASK_FINISHED)
            channel.deliver(2, StatusCode.TASK_ABORTED)
            return await asyncio.wait_for(asyncio.gather(a, b, c), 1.0)

    first, second, third = run(scenario())
    assert (first.uid, second.uid, third.uid) == (1, 2, 3)
    assert second.status == StatusCode.TASK_ABORTED   # uid 2 was the aborted one
    assert third.is_finished


def test_repeat_launches_of_one_uid_are_matched_fifo():
    async def scenario():
        channel = FakeChannel()
        async with Client(channel, uid_bytes=UID_BYTES) as client:
            first = client.launch(7, args=b"\x01")
            second = client.launch(7, args=b"\x02")
            channel.deliver(7, StatusCode.TASK_FINISHED, b"\xaa")
            channel.deliver(7, StatusCode.TASK_FINISHED, b"\xbb")
            return await asyncio.wait_for(asyncio.gather(first, second), 1.0)

    first, second = run(scenario())
    assert (first.result[0], second.result[0]) == (0xAA, 0xBB)


def test_a_rejection_resolves_the_launch_it_answers():
    async def scenario():
        channel = FakeChannel()
        async with Client(channel, uid_bytes=UID_BYTES) as client:
            pending = client.launch(9)
            channel.deliver(9, StatusCode.TASK_UNKNOWN)
            return await asyncio.wait_for(pending, 1.0)

    reply = run(scenario())
    assert reply.is_rejection and reply.status == StatusCode.TASK_UNKNOWN


# -----------------------
# Commands
# -----------------------

def test_pause_resume_and_complete_send_their_operations():
    async def scenario():
        channel = FakeChannel()
        async with Client(channel, uid_bytes=UID_BYTES) as client:
            client.pause(4)
            client.resume(4)
            client.complete(4)
            await settle()
        return channel.sent

    sent = run(scenario())
    commands = [Directive.unpack(p.payload[0]).command for p in sent]
    assert commands == [Operation.PAUSE_TASK, Operation.RESUME_TASK, Operation.COMPLETE_TASK]
    assert Directive.unpack(sent[2].payload[0]).reason == 1  # aborted


def test_a_failed_command_reaches_on_error():
    # pause/resume/complete succeed silently; only failures come back, and with
    # nothing outstanding for that uid they are routed to on_error.
    async def scenario():
        seen = []
        channel = FakeChannel()
        async with Client(channel, uid_bytes=UID_BYTES, on_error=seen.append) as client:
            client.pause(4)
            channel.deliver(4, StatusCode.TASK_NOT_RUNNING)
            await settle()
        return seen

    seen = run(scenario())
    assert len(seen) == 1 and seen[0].status == StatusCode.TASK_NOT_RUNNING


def test_a_completion_nobody_awaits_reaches_on_orphan():
    async def scenario():
        seen = []
        channel = FakeChannel()
        async with Client(channel, uid_bytes=UID_BYTES, on_orphan=seen.append) as client:
            channel.deliver(5, StatusCode.TASK_FINISHED, b"\x01")
            await settle()
        return seen

    seen = run(scenario())
    assert len(seen) == 1 and seen[0].uid == 5


# -----------------------
# Giving up, and shutting down
# -----------------------

def test_a_timed_out_launch_does_not_desync_the_queue():
    # If a caller gives up, its slot must leave the queue - otherwise the next
    # reply would resolve the dead future and every later call of this uid would
    # be one reply behind.
    async def scenario():
        channel = FakeChannel()
        async with Client(channel, uid_bytes=UID_BYTES) as client:
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(client.launch(7), 0.01)
            second = client.launch(7, args=b"\x02")
            channel.deliver(7, StatusCode.TASK_FINISHED, b"\xbb")
            return await asyncio.wait_for(second, 1.0)

    reply = run(scenario())
    assert reply.result[0] == 0xBB


def test_closing_fails_everything_still_waiting():
    async def scenario():
        channel = FakeChannel()
        client = Client(channel, uid_bytes=UID_BYTES)
        client.start()
        pending = client.launch(7)
        await client.aclose()
        return pending

    pending = run(scenario())
    with pytest.raises(ClientClosed):
        pending.result()


def test_launching_after_close_is_refused():
    async def scenario():
        channel = FakeChannel()
        client = Client(channel, uid_bytes=UID_BYTES)
        client.start()
        await client.aclose()
        with pytest.raises(ClientClosed):
            client.launch(7)

    run(scenario())
