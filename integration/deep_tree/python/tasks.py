"""Generated etask client bindings - do not edit.

Regenerated from the project's schema on every `etask generate --python`
run; 294 task(s).

Each task is an awaitable call whose result is one of its declared
shapes, chosen by the status code the reply carries::

    async with Client(channel, uid_bytes=UID_BYTES,
                      fingerprint=SCHEMA_FINGERPRINT) as client:
        tasks = Tasks(client)
        result = await tasks.<scope>.<task>(<params>)

Launching does not block: start several tasks and await them together
with `asyncio.gather`. See `etask.client` for how replies are matched.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from etask.binding import (
    InstantTaskBinding,
    Scope,
    TaskBinding,
    UndeclaredResult,
    build_shapes,
)
from etask.client import Client

UID_BYTES = 2
"""Width of a task uid on the wire, pinned by the project's uid ledger."""

SCHEMA_FINGERPRINT = 0x570C5302C06F6996
"""The wire contract this client speaks, as eight bytes.

Covers every uid, argument list, result shape and link policy in the
schema this was generated from. The device sends its own at connect; if
the two differ, the peers were built from different schemas and the
client refuses the link rather than trading frames whose uids it would
misread.
"""


class TaskId(IntEnum):
    """Every task's wire uid - the same values as `global::task_id` in C++."""

    MESH_S0_N0_P0_SAMPLE = 9
    MESH_S0_N0_P0_ARM = 6
    MESH_S0_N0_P0_HOLD = 7
    MESH_S0_N0_P0_QUENCH = 8
    MESH_S0_N0_P1_SAMPLE = 13
    MESH_S0_N0_P1_ARM = 10
    MESH_S0_N0_P1_HOLD = 11
    MESH_S0_N0_P1_QUENCH = 12
    MESH_S0_N0_P2_SAMPLE = 17
    MESH_S0_N0_P2_ARM = 14
    MESH_S0_N0_P2_HOLD = 15
    MESH_S0_N0_P2_QUENCH = 16
    MESH_S0_N1_P0_SAMPLE = 21
    MESH_S0_N1_P0_ARM = 18
    MESH_S0_N1_P0_HOLD = 19
    MESH_S0_N1_P0_QUENCH = 20
    MESH_S0_N1_P1_SAMPLE = 25
    MESH_S0_N1_P1_ARM = 22
    MESH_S0_N1_P1_HOLD = 23
    MESH_S0_N1_P1_QUENCH = 24
    MESH_S0_N1_P2_SAMPLE = 29
    MESH_S0_N1_P2_ARM = 26
    MESH_S0_N1_P2_HOLD = 27
    MESH_S0_N1_P2_QUENCH = 28
    MESH_S0_N2_P0_SAMPLE = 33
    MESH_S0_N2_P0_ARM = 30
    MESH_S0_N2_P0_HOLD = 31
    MESH_S0_N2_P0_QUENCH = 32
    MESH_S0_N2_P1_SAMPLE = 37
    MESH_S0_N2_P1_ARM = 34
    MESH_S0_N2_P1_HOLD = 35
    MESH_S0_N2_P1_QUENCH = 36
    MESH_S0_N2_P2_SAMPLE = 41
    MESH_S0_N2_P2_ARM = 38
    MESH_S0_N2_P2_HOLD = 39
    MESH_S0_N2_P2_QUENCH = 40
    MESH_S0_N3_P0_SAMPLE = 45
    MESH_S0_N3_P0_ARM = 42
    MESH_S0_N3_P0_HOLD = 43
    MESH_S0_N3_P0_QUENCH = 44
    MESH_S0_N3_P1_SAMPLE = 49
    MESH_S0_N3_P1_ARM = 46
    MESH_S0_N3_P1_HOLD = 47
    MESH_S0_N3_P1_QUENCH = 48
    MESH_S0_N3_P2_SAMPLE = 53
    MESH_S0_N3_P2_ARM = 50
    MESH_S0_N3_P2_HOLD = 51
    MESH_S0_N3_P2_QUENCH = 52
    MESH_S1_N0_P0_SAMPLE = 57
    MESH_S1_N0_P0_ARM = 54
    MESH_S1_N0_P0_HOLD = 55
    MESH_S1_N0_P0_QUENCH = 56
    MESH_S1_N0_P1_SAMPLE = 61
    MESH_S1_N0_P1_ARM = 58
    MESH_S1_N0_P1_HOLD = 59
    MESH_S1_N0_P1_QUENCH = 60
    MESH_S1_N0_P2_SAMPLE = 65
    MESH_S1_N0_P2_ARM = 62
    MESH_S1_N0_P2_HOLD = 63
    MESH_S1_N0_P2_QUENCH = 64
    MESH_S1_N1_P0_SAMPLE = 69
    MESH_S1_N1_P0_ARM = 66
    MESH_S1_N1_P0_HOLD = 67
    MESH_S1_N1_P0_QUENCH = 68
    MESH_S1_N1_P1_SAMPLE = 73
    MESH_S1_N1_P1_ARM = 70
    MESH_S1_N1_P1_HOLD = 71
    MESH_S1_N1_P1_QUENCH = 72
    MESH_S1_N1_P2_SAMPLE = 77
    MESH_S1_N1_P2_ARM = 74
    MESH_S1_N1_P2_HOLD = 75
    MESH_S1_N1_P2_QUENCH = 76
    MESH_S1_N2_P0_SAMPLE = 81
    MESH_S1_N2_P0_ARM = 78
    MESH_S1_N2_P0_HOLD = 79
    MESH_S1_N2_P0_QUENCH = 80
    MESH_S1_N2_P1_SAMPLE = 85
    MESH_S1_N2_P1_ARM = 82
    MESH_S1_N2_P1_HOLD = 83
    MESH_S1_N2_P1_QUENCH = 84
    MESH_S1_N2_P2_SAMPLE = 89
    MESH_S1_N2_P2_ARM = 86
    MESH_S1_N2_P2_HOLD = 87
    MESH_S1_N2_P2_QUENCH = 88
    MESH_S1_N3_P0_SAMPLE = 93
    MESH_S1_N3_P0_ARM = 90
    MESH_S1_N3_P0_HOLD = 91
    MESH_S1_N3_P0_QUENCH = 92
    MESH_S1_N3_P1_SAMPLE = 97
    MESH_S1_N3_P1_ARM = 94
    MESH_S1_N3_P1_HOLD = 95
    MESH_S1_N3_P1_QUENCH = 96
    MESH_S1_N3_P2_SAMPLE = 101
    MESH_S1_N3_P2_ARM = 98
    MESH_S1_N3_P2_HOLD = 99
    MESH_S1_N3_P2_QUENCH = 100
    MESH_S2_N0_P0_SAMPLE = 105
    MESH_S2_N0_P0_ARM = 102
    MESH_S2_N0_P0_HOLD = 103
    MESH_S2_N0_P0_QUENCH = 104
    MESH_S2_N0_P1_SAMPLE = 109
    MESH_S2_N0_P1_ARM = 106
    MESH_S2_N0_P1_HOLD = 107
    MESH_S2_N0_P1_QUENCH = 108
    MESH_S2_N0_P2_SAMPLE = 113
    MESH_S2_N0_P2_ARM = 110
    MESH_S2_N0_P2_HOLD = 111
    MESH_S2_N0_P2_QUENCH = 112
    MESH_S2_N1_P0_SAMPLE = 117
    MESH_S2_N1_P0_ARM = 114
    MESH_S2_N1_P0_HOLD = 115
    MESH_S2_N1_P0_QUENCH = 116
    MESH_S2_N1_P1_SAMPLE = 121
    MESH_S2_N1_P1_ARM = 118
    MESH_S2_N1_P1_HOLD = 119
    MESH_S2_N1_P1_QUENCH = 120
    MESH_S2_N1_P2_SAMPLE = 125
    MESH_S2_N1_P2_ARM = 122
    MESH_S2_N1_P2_HOLD = 123
    MESH_S2_N1_P2_QUENCH = 124
    MESH_S2_N2_P0_SAMPLE = 129
    MESH_S2_N2_P0_ARM = 126
    MESH_S2_N2_P0_HOLD = 127
    MESH_S2_N2_P0_QUENCH = 128
    MESH_S2_N2_P1_SAMPLE = 133
    MESH_S2_N2_P1_ARM = 130
    MESH_S2_N2_P1_HOLD = 131
    MESH_S2_N2_P1_QUENCH = 132
    MESH_S2_N2_P2_SAMPLE = 137
    MESH_S2_N2_P2_ARM = 134
    MESH_S2_N2_P2_HOLD = 135
    MESH_S2_N2_P2_QUENCH = 136
    MESH_S2_N3_P0_SAMPLE = 141
    MESH_S2_N3_P0_ARM = 138
    MESH_S2_N3_P0_HOLD = 139
    MESH_S2_N3_P0_QUENCH = 140
    MESH_S2_N3_P1_SAMPLE = 145
    MESH_S2_N3_P1_ARM = 142
    MESH_S2_N3_P1_HOLD = 143
    MESH_S2_N3_P1_QUENCH = 144
    MESH_S2_N3_P2_SAMPLE = 149
    MESH_S2_N3_P2_ARM = 146
    MESH_S2_N3_P2_HOLD = 147
    MESH_S2_N3_P2_QUENCH = 148
    MESH_S3_N0_P0_SAMPLE = 153
    MESH_S3_N0_P0_ARM = 150
    MESH_S3_N0_P0_HOLD = 151
    MESH_S3_N0_P0_QUENCH = 152
    MESH_S3_N0_P1_SAMPLE = 157
    MESH_S3_N0_P1_ARM = 154
    MESH_S3_N0_P1_HOLD = 155
    MESH_S3_N0_P1_QUENCH = 156
    MESH_S3_N0_P2_SAMPLE = 161
    MESH_S3_N0_P2_ARM = 158
    MESH_S3_N0_P2_HOLD = 159
    MESH_S3_N0_P2_QUENCH = 160
    MESH_S3_N1_P0_SAMPLE = 165
    MESH_S3_N1_P0_ARM = 162
    MESH_S3_N1_P0_HOLD = 163
    MESH_S3_N1_P0_QUENCH = 164
    MESH_S3_N1_P1_SAMPLE = 169
    MESH_S3_N1_P1_ARM = 166
    MESH_S3_N1_P1_HOLD = 167
    MESH_S3_N1_P1_QUENCH = 168
    MESH_S3_N1_P2_SAMPLE = 173
    MESH_S3_N1_P2_ARM = 170
    MESH_S3_N1_P2_HOLD = 171
    MESH_S3_N1_P2_QUENCH = 172
    MESH_S3_N2_P0_SAMPLE = 177
    MESH_S3_N2_P0_ARM = 174
    MESH_S3_N2_P0_HOLD = 175
    MESH_S3_N2_P0_QUENCH = 176
    MESH_S3_N2_P1_SAMPLE = 181
    MESH_S3_N2_P1_ARM = 178
    MESH_S3_N2_P1_HOLD = 179
    MESH_S3_N2_P1_QUENCH = 180
    MESH_S3_N2_P2_SAMPLE = 185
    MESH_S3_N2_P2_ARM = 182
    MESH_S3_N2_P2_HOLD = 183
    MESH_S3_N2_P2_QUENCH = 184
    MESH_S3_N3_P0_SAMPLE = 189
    MESH_S3_N3_P0_ARM = 186
    MESH_S3_N3_P0_HOLD = 187
    MESH_S3_N3_P0_QUENCH = 188
    MESH_S3_N3_P1_SAMPLE = 193
    MESH_S3_N3_P1_ARM = 190
    MESH_S3_N3_P1_HOLD = 191
    MESH_S3_N3_P1_QUENCH = 192
    MESH_S3_N3_P2_SAMPLE = 197
    MESH_S3_N3_P2_ARM = 194
    MESH_S3_N3_P2_HOLD = 195
    MESH_S3_N3_P2_QUENCH = 196
    MESH_S4_N0_P0_SAMPLE = 201
    MESH_S4_N0_P0_ARM = 198
    MESH_S4_N0_P0_HOLD = 199
    MESH_S4_N0_P0_QUENCH = 200
    MESH_S4_N0_P1_SAMPLE = 205
    MESH_S4_N0_P1_ARM = 202
    MESH_S4_N0_P1_HOLD = 203
    MESH_S4_N0_P1_QUENCH = 204
    MESH_S4_N0_P2_SAMPLE = 209
    MESH_S4_N0_P2_ARM = 206
    MESH_S4_N0_P2_HOLD = 207
    MESH_S4_N0_P2_QUENCH = 208
    MESH_S4_N1_P0_SAMPLE = 213
    MESH_S4_N1_P0_ARM = 210
    MESH_S4_N1_P0_HOLD = 211
    MESH_S4_N1_P0_QUENCH = 212
    MESH_S4_N1_P1_SAMPLE = 217
    MESH_S4_N1_P1_ARM = 214
    MESH_S4_N1_P1_HOLD = 215
    MESH_S4_N1_P1_QUENCH = 216
    MESH_S4_N1_P2_SAMPLE = 221
    MESH_S4_N1_P2_ARM = 218
    MESH_S4_N1_P2_HOLD = 219
    MESH_S4_N1_P2_QUENCH = 220
    MESH_S4_N2_P0_SAMPLE = 225
    MESH_S4_N2_P0_ARM = 222
    MESH_S4_N2_P0_HOLD = 223
    MESH_S4_N2_P0_QUENCH = 224
    MESH_S4_N2_P1_SAMPLE = 229
    MESH_S4_N2_P1_ARM = 226
    MESH_S4_N2_P1_HOLD = 227
    MESH_S4_N2_P1_QUENCH = 228
    MESH_S4_N2_P2_SAMPLE = 233
    MESH_S4_N2_P2_ARM = 230
    MESH_S4_N2_P2_HOLD = 231
    MESH_S4_N2_P2_QUENCH = 232
    MESH_S4_N3_P0_SAMPLE = 237
    MESH_S4_N3_P0_ARM = 234
    MESH_S4_N3_P0_HOLD = 235
    MESH_S4_N3_P0_QUENCH = 236
    MESH_S4_N3_P1_SAMPLE = 241
    MESH_S4_N3_P1_ARM = 238
    MESH_S4_N3_P1_HOLD = 239
    MESH_S4_N3_P1_QUENCH = 240
    MESH_S4_N3_P2_SAMPLE = 245
    MESH_S4_N3_P2_ARM = 242
    MESH_S4_N3_P2_HOLD = 243
    MESH_S4_N3_P2_QUENCH = 244
    MESH_S5_N0_P0_SAMPLE = 249
    MESH_S5_N0_P0_ARM = 246
    MESH_S5_N0_P0_HOLD = 247
    MESH_S5_N0_P0_QUENCH = 248
    MESH_S5_N0_P1_SAMPLE = 253
    MESH_S5_N0_P1_ARM = 250
    MESH_S5_N0_P1_HOLD = 251
    MESH_S5_N0_P1_QUENCH = 252
    MESH_S5_N0_P2_SAMPLE = 257
    MESH_S5_N0_P2_ARM = 254
    MESH_S5_N0_P2_HOLD = 255
    MESH_S5_N0_P2_QUENCH = 256
    MESH_S5_N1_P0_SAMPLE = 261
    MESH_S5_N1_P0_ARM = 258
    MESH_S5_N1_P0_HOLD = 259
    MESH_S5_N1_P0_QUENCH = 260
    MESH_S5_N1_P1_SAMPLE = 265
    MESH_S5_N1_P1_ARM = 262
    MESH_S5_N1_P1_HOLD = 263
    MESH_S5_N1_P1_QUENCH = 264
    MESH_S5_N1_P2_SAMPLE = 269
    MESH_S5_N1_P2_ARM = 266
    MESH_S5_N1_P2_HOLD = 267
    MESH_S5_N1_P2_QUENCH = 268
    MESH_S5_N2_P0_SAMPLE = 273
    MESH_S5_N2_P0_ARM = 270
    MESH_S5_N2_P0_HOLD = 271
    MESH_S5_N2_P0_QUENCH = 272
    MESH_S5_N2_P1_SAMPLE = 277
    MESH_S5_N2_P1_ARM = 274
    MESH_S5_N2_P1_HOLD = 275
    MESH_S5_N2_P1_QUENCH = 276
    MESH_S5_N2_P2_SAMPLE = 281
    MESH_S5_N2_P2_ARM = 278
    MESH_S5_N2_P2_HOLD = 279
    MESH_S5_N2_P2_QUENCH = 280
    MESH_S5_N3_P0_SAMPLE = 285
    MESH_S5_N3_P0_ARM = 282
    MESH_S5_N3_P0_HOLD = 283
    MESH_S5_N3_P0_QUENCH = 284
    MESH_S5_N3_P1_SAMPLE = 289
    MESH_S5_N3_P1_ARM = 286
    MESH_S5_N3_P1_HOLD = 287
    MESH_S5_N3_P1_QUENCH = 288
    MESH_S5_N3_P2_SAMPLE = 293
    MESH_S5_N3_P2_ARM = 290
    MESH_S5_N3_P2_HOLD = 291
    MESH_S5_N3_P2_QUENCH = 292
    BUS_LINK_STATE_PROBE = 1
    BUS_LINK_STATE_PROBE2 = 0
    BUS_RESERVE_EMERGENCY_HALT = 4
    BUS_RESERVE_DIAGNOSTIC = 3
    BUS_RESERVE_AUDIT = 2
    CENSUS = 5




@dataclass(frozen=True)
class MeshS0N0P0SampleFinished:
    """`mesh.s0.n0.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N0P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s0.n0.p0.sample`, uid 9.

    Returns one of:
      - `MeshS0N0P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N0_P0_SAMPLE
    PATH = "mesh.s0.n0.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N0P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS0N0P0SampleFinished

    async def __call__(self) -> MeshS0N0P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s0.n0.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS0N0P0ArmFinished:
    """`mesh.s0.n0.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N0P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s0.n0.p0.arm`, uid 6.

    Returns one of:
      - `MeshS0N0P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N0_P0_ARM
    PATH = "mesh.s0.n0.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS0N0P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS0N0P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS0N0P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s0.n0.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS0N0P0HoldFinished:
    """`mesh.s0.n0.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N0P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s0.n0.p0.hold`, uid 7.

    Returns one of:
      - `MeshS0N0P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N0_P0_HOLD
    PATH = "mesh.s0.n0.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N0P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS0N0P0HoldFinished

    async def __call__(self) -> MeshS0N0P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s0.n0.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS0N0P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s0.n0.p0.quench`, uid 8.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S0_N0_P0_QUENCH
    PATH = "mesh.s0.n0.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s0.n0.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS0N0P1SampleFinished:
    """`mesh.s0.n0.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N0P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s0.n0.p1.sample`, uid 13.

    Returns one of:
      - `MeshS0N0P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N0_P1_SAMPLE
    PATH = "mesh.s0.n0.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N0P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS0N0P1SampleFinished

    async def __call__(self) -> MeshS0N0P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s0.n0.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS0N0P1ArmFinished:
    """`mesh.s0.n0.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N0P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s0.n0.p1.arm`, uid 10.

    Returns one of:
      - `MeshS0N0P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N0_P1_ARM
    PATH = "mesh.s0.n0.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS0N0P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS0N0P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS0N0P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s0.n0.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS0N0P1HoldFinished:
    """`mesh.s0.n0.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N0P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s0.n0.p1.hold`, uid 11.

    Returns one of:
      - `MeshS0N0P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N0_P1_HOLD
    PATH = "mesh.s0.n0.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N0P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS0N0P1HoldFinished

    async def __call__(self) -> MeshS0N0P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s0.n0.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS0N0P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s0.n0.p1.quench`, uid 12.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S0_N0_P1_QUENCH
    PATH = "mesh.s0.n0.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s0.n0.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS0N0P2SampleFinished:
    """`mesh.s0.n0.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N0P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s0.n0.p2.sample`, uid 17.

    Returns one of:
      - `MeshS0N0P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N0_P2_SAMPLE
    PATH = "mesh.s0.n0.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N0P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS0N0P2SampleFinished

    async def __call__(self) -> MeshS0N0P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s0.n0.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS0N0P2ArmFinished:
    """`mesh.s0.n0.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N0P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s0.n0.p2.arm`, uid 14.

    Returns one of:
      - `MeshS0N0P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N0_P2_ARM
    PATH = "mesh.s0.n0.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS0N0P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS0N0P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS0N0P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s0.n0.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS0N0P2HoldFinished:
    """`mesh.s0.n0.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N0P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s0.n0.p2.hold`, uid 15.

    Returns one of:
      - `MeshS0N0P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N0_P2_HOLD
    PATH = "mesh.s0.n0.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N0P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS0N0P2HoldFinished

    async def __call__(self) -> MeshS0N0P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s0.n0.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS0N0P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s0.n0.p2.quench`, uid 16.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S0_N0_P2_QUENCH
    PATH = "mesh.s0.n0.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s0.n0.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS0N1P0SampleFinished:
    """`mesh.s0.n1.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N1P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s0.n1.p0.sample`, uid 21.

    Returns one of:
      - `MeshS0N1P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N1_P0_SAMPLE
    PATH = "mesh.s0.n1.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N1P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS0N1P0SampleFinished

    async def __call__(self) -> MeshS0N1P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s0.n1.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS0N1P0ArmFinished:
    """`mesh.s0.n1.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N1P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s0.n1.p0.arm`, uid 18.

    Returns one of:
      - `MeshS0N1P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N1_P0_ARM
    PATH = "mesh.s0.n1.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS0N1P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS0N1P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS0N1P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s0.n1.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS0N1P0HoldFinished:
    """`mesh.s0.n1.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N1P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s0.n1.p0.hold`, uid 19.

    Returns one of:
      - `MeshS0N1P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N1_P0_HOLD
    PATH = "mesh.s0.n1.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N1P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS0N1P0HoldFinished

    async def __call__(self) -> MeshS0N1P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s0.n1.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS0N1P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s0.n1.p0.quench`, uid 20.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S0_N1_P0_QUENCH
    PATH = "mesh.s0.n1.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s0.n1.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS0N1P1SampleFinished:
    """`mesh.s0.n1.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N1P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s0.n1.p1.sample`, uid 25.

    Returns one of:
      - `MeshS0N1P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N1_P1_SAMPLE
    PATH = "mesh.s0.n1.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N1P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS0N1P1SampleFinished

    async def __call__(self) -> MeshS0N1P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s0.n1.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS0N1P1ArmFinished:
    """`mesh.s0.n1.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N1P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s0.n1.p1.arm`, uid 22.

    Returns one of:
      - `MeshS0N1P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N1_P1_ARM
    PATH = "mesh.s0.n1.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS0N1P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS0N1P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS0N1P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s0.n1.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS0N1P1HoldFinished:
    """`mesh.s0.n1.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N1P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s0.n1.p1.hold`, uid 23.

    Returns one of:
      - `MeshS0N1P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N1_P1_HOLD
    PATH = "mesh.s0.n1.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N1P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS0N1P1HoldFinished

    async def __call__(self) -> MeshS0N1P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s0.n1.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS0N1P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s0.n1.p1.quench`, uid 24.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S0_N1_P1_QUENCH
    PATH = "mesh.s0.n1.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s0.n1.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS0N1P2SampleFinished:
    """`mesh.s0.n1.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N1P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s0.n1.p2.sample`, uid 29.

    Returns one of:
      - `MeshS0N1P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N1_P2_SAMPLE
    PATH = "mesh.s0.n1.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N1P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS0N1P2SampleFinished

    async def __call__(self) -> MeshS0N1P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s0.n1.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS0N1P2ArmFinished:
    """`mesh.s0.n1.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N1P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s0.n1.p2.arm`, uid 26.

    Returns one of:
      - `MeshS0N1P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N1_P2_ARM
    PATH = "mesh.s0.n1.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS0N1P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS0N1P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS0N1P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s0.n1.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS0N1P2HoldFinished:
    """`mesh.s0.n1.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N1P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s0.n1.p2.hold`, uid 27.

    Returns one of:
      - `MeshS0N1P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N1_P2_HOLD
    PATH = "mesh.s0.n1.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N1P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS0N1P2HoldFinished

    async def __call__(self) -> MeshS0N1P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s0.n1.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS0N1P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s0.n1.p2.quench`, uid 28.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S0_N1_P2_QUENCH
    PATH = "mesh.s0.n1.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s0.n1.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS0N2P0SampleFinished:
    """`mesh.s0.n2.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N2P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s0.n2.p0.sample`, uid 33.

    Returns one of:
      - `MeshS0N2P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N2_P0_SAMPLE
    PATH = "mesh.s0.n2.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N2P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS0N2P0SampleFinished

    async def __call__(self) -> MeshS0N2P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s0.n2.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS0N2P0ArmFinished:
    """`mesh.s0.n2.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N2P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s0.n2.p0.arm`, uid 30.

    Returns one of:
      - `MeshS0N2P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N2_P0_ARM
    PATH = "mesh.s0.n2.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS0N2P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS0N2P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS0N2P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s0.n2.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS0N2P0HoldFinished:
    """`mesh.s0.n2.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N2P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s0.n2.p0.hold`, uid 31.

    Returns one of:
      - `MeshS0N2P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N2_P0_HOLD
    PATH = "mesh.s0.n2.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N2P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS0N2P0HoldFinished

    async def __call__(self) -> MeshS0N2P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s0.n2.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS0N2P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s0.n2.p0.quench`, uid 32.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S0_N2_P0_QUENCH
    PATH = "mesh.s0.n2.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s0.n2.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS0N2P1SampleFinished:
    """`mesh.s0.n2.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N2P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s0.n2.p1.sample`, uid 37.

    Returns one of:
      - `MeshS0N2P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N2_P1_SAMPLE
    PATH = "mesh.s0.n2.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N2P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS0N2P1SampleFinished

    async def __call__(self) -> MeshS0N2P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s0.n2.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS0N2P1ArmFinished:
    """`mesh.s0.n2.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N2P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s0.n2.p1.arm`, uid 34.

    Returns one of:
      - `MeshS0N2P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N2_P1_ARM
    PATH = "mesh.s0.n2.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS0N2P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS0N2P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS0N2P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s0.n2.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS0N2P1HoldFinished:
    """`mesh.s0.n2.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N2P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s0.n2.p1.hold`, uid 35.

    Returns one of:
      - `MeshS0N2P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N2_P1_HOLD
    PATH = "mesh.s0.n2.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N2P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS0N2P1HoldFinished

    async def __call__(self) -> MeshS0N2P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s0.n2.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS0N2P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s0.n2.p1.quench`, uid 36.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S0_N2_P1_QUENCH
    PATH = "mesh.s0.n2.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s0.n2.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS0N2P2SampleFinished:
    """`mesh.s0.n2.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N2P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s0.n2.p2.sample`, uid 41.

    Returns one of:
      - `MeshS0N2P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N2_P2_SAMPLE
    PATH = "mesh.s0.n2.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N2P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS0N2P2SampleFinished

    async def __call__(self) -> MeshS0N2P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s0.n2.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS0N2P2ArmFinished:
    """`mesh.s0.n2.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N2P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s0.n2.p2.arm`, uid 38.

    Returns one of:
      - `MeshS0N2P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N2_P2_ARM
    PATH = "mesh.s0.n2.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS0N2P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS0N2P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS0N2P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s0.n2.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS0N2P2HoldFinished:
    """`mesh.s0.n2.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N2P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s0.n2.p2.hold`, uid 39.

    Returns one of:
      - `MeshS0N2P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N2_P2_HOLD
    PATH = "mesh.s0.n2.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N2P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS0N2P2HoldFinished

    async def __call__(self) -> MeshS0N2P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s0.n2.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS0N2P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s0.n2.p2.quench`, uid 40.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S0_N2_P2_QUENCH
    PATH = "mesh.s0.n2.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s0.n2.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS0N3P0SampleFinished:
    """`mesh.s0.n3.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N3P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s0.n3.p0.sample`, uid 45.

    Returns one of:
      - `MeshS0N3P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N3_P0_SAMPLE
    PATH = "mesh.s0.n3.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N3P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS0N3P0SampleFinished

    async def __call__(self) -> MeshS0N3P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s0.n3.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS0N3P0ArmFinished:
    """`mesh.s0.n3.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N3P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s0.n3.p0.arm`, uid 42.

    Returns one of:
      - `MeshS0N3P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N3_P0_ARM
    PATH = "mesh.s0.n3.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS0N3P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS0N3P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS0N3P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s0.n3.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS0N3P0HoldFinished:
    """`mesh.s0.n3.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N3P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s0.n3.p0.hold`, uid 43.

    Returns one of:
      - `MeshS0N3P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N3_P0_HOLD
    PATH = "mesh.s0.n3.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N3P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS0N3P0HoldFinished

    async def __call__(self) -> MeshS0N3P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s0.n3.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS0N3P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s0.n3.p0.quench`, uid 44.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S0_N3_P0_QUENCH
    PATH = "mesh.s0.n3.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s0.n3.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS0N3P1SampleFinished:
    """`mesh.s0.n3.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N3P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s0.n3.p1.sample`, uid 49.

    Returns one of:
      - `MeshS0N3P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N3_P1_SAMPLE
    PATH = "mesh.s0.n3.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N3P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS0N3P1SampleFinished

    async def __call__(self) -> MeshS0N3P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s0.n3.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS0N3P1ArmFinished:
    """`mesh.s0.n3.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N3P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s0.n3.p1.arm`, uid 46.

    Returns one of:
      - `MeshS0N3P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N3_P1_ARM
    PATH = "mesh.s0.n3.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS0N3P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS0N3P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS0N3P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s0.n3.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS0N3P1HoldFinished:
    """`mesh.s0.n3.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N3P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s0.n3.p1.hold`, uid 47.

    Returns one of:
      - `MeshS0N3P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N3_P1_HOLD
    PATH = "mesh.s0.n3.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N3P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS0N3P1HoldFinished

    async def __call__(self) -> MeshS0N3P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s0.n3.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS0N3P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s0.n3.p1.quench`, uid 48.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S0_N3_P1_QUENCH
    PATH = "mesh.s0.n3.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s0.n3.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS0N3P2SampleFinished:
    """`mesh.s0.n3.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N3P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s0.n3.p2.sample`, uid 53.

    Returns one of:
      - `MeshS0N3P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N3_P2_SAMPLE
    PATH = "mesh.s0.n3.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N3P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS0N3P2SampleFinished

    async def __call__(self) -> MeshS0N3P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s0.n3.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS0N3P2ArmFinished:
    """`mesh.s0.n3.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N3P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s0.n3.p2.arm`, uid 50.

    Returns one of:
      - `MeshS0N3P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N3_P2_ARM
    PATH = "mesh.s0.n3.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS0N3P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS0N3P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS0N3P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s0.n3.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS0N3P2HoldFinished:
    """`mesh.s0.n3.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N3P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s0.n3.p2.hold`, uid 51.

    Returns one of:
      - `MeshS0N3P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S0_N3_P2_HOLD
    PATH = "mesh.s0.n3.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS0N3P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS0N3P2HoldFinished

    async def __call__(self) -> MeshS0N3P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s0.n3.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS0N3P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s0.n3.p2.quench`, uid 52.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S0_N3_P2_QUENCH
    PATH = "mesh.s0.n3.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s0.n3.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS1N0P0SampleFinished:
    """`mesh.s1.n0.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N0P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s1.n0.p0.sample`, uid 57.

    Returns one of:
      - `MeshS1N0P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N0_P0_SAMPLE
    PATH = "mesh.s1.n0.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N0P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS1N0P0SampleFinished

    async def __call__(self) -> MeshS1N0P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s1.n0.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS1N0P0ArmFinished:
    """`mesh.s1.n0.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N0P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s1.n0.p0.arm`, uid 54.

    Returns one of:
      - `MeshS1N0P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N0_P0_ARM
    PATH = "mesh.s1.n0.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS1N0P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS1N0P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS1N0P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s1.n0.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS1N0P0HoldFinished:
    """`mesh.s1.n0.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N0P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s1.n0.p0.hold`, uid 55.

    Returns one of:
      - `MeshS1N0P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N0_P0_HOLD
    PATH = "mesh.s1.n0.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N0P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS1N0P0HoldFinished

    async def __call__(self) -> MeshS1N0P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s1.n0.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS1N0P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s1.n0.p0.quench`, uid 56.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S1_N0_P0_QUENCH
    PATH = "mesh.s1.n0.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s1.n0.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS1N0P1SampleFinished:
    """`mesh.s1.n0.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N0P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s1.n0.p1.sample`, uid 61.

    Returns one of:
      - `MeshS1N0P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N0_P1_SAMPLE
    PATH = "mesh.s1.n0.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N0P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS1N0P1SampleFinished

    async def __call__(self) -> MeshS1N0P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s1.n0.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS1N0P1ArmFinished:
    """`mesh.s1.n0.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N0P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s1.n0.p1.arm`, uid 58.

    Returns one of:
      - `MeshS1N0P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N0_P1_ARM
    PATH = "mesh.s1.n0.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS1N0P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS1N0P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS1N0P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s1.n0.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS1N0P1HoldFinished:
    """`mesh.s1.n0.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N0P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s1.n0.p1.hold`, uid 59.

    Returns one of:
      - `MeshS1N0P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N0_P1_HOLD
    PATH = "mesh.s1.n0.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N0P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS1N0P1HoldFinished

    async def __call__(self) -> MeshS1N0P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s1.n0.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS1N0P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s1.n0.p1.quench`, uid 60.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S1_N0_P1_QUENCH
    PATH = "mesh.s1.n0.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s1.n0.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS1N0P2SampleFinished:
    """`mesh.s1.n0.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N0P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s1.n0.p2.sample`, uid 65.

    Returns one of:
      - `MeshS1N0P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N0_P2_SAMPLE
    PATH = "mesh.s1.n0.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N0P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS1N0P2SampleFinished

    async def __call__(self) -> MeshS1N0P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s1.n0.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS1N0P2ArmFinished:
    """`mesh.s1.n0.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N0P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s1.n0.p2.arm`, uid 62.

    Returns one of:
      - `MeshS1N0P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N0_P2_ARM
    PATH = "mesh.s1.n0.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS1N0P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS1N0P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS1N0P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s1.n0.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS1N0P2HoldFinished:
    """`mesh.s1.n0.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N0P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s1.n0.p2.hold`, uid 63.

    Returns one of:
      - `MeshS1N0P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N0_P2_HOLD
    PATH = "mesh.s1.n0.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N0P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS1N0P2HoldFinished

    async def __call__(self) -> MeshS1N0P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s1.n0.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS1N0P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s1.n0.p2.quench`, uid 64.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S1_N0_P2_QUENCH
    PATH = "mesh.s1.n0.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s1.n0.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS1N1P0SampleFinished:
    """`mesh.s1.n1.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N1P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s1.n1.p0.sample`, uid 69.

    Returns one of:
      - `MeshS1N1P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N1_P0_SAMPLE
    PATH = "mesh.s1.n1.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N1P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS1N1P0SampleFinished

    async def __call__(self) -> MeshS1N1P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s1.n1.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS1N1P0ArmFinished:
    """`mesh.s1.n1.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N1P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s1.n1.p0.arm`, uid 66.

    Returns one of:
      - `MeshS1N1P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N1_P0_ARM
    PATH = "mesh.s1.n1.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS1N1P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS1N1P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS1N1P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s1.n1.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS1N1P0HoldFinished:
    """`mesh.s1.n1.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N1P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s1.n1.p0.hold`, uid 67.

    Returns one of:
      - `MeshS1N1P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N1_P0_HOLD
    PATH = "mesh.s1.n1.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N1P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS1N1P0HoldFinished

    async def __call__(self) -> MeshS1N1P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s1.n1.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS1N1P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s1.n1.p0.quench`, uid 68.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S1_N1_P0_QUENCH
    PATH = "mesh.s1.n1.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s1.n1.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS1N1P1SampleFinished:
    """`mesh.s1.n1.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N1P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s1.n1.p1.sample`, uid 73.

    Returns one of:
      - `MeshS1N1P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N1_P1_SAMPLE
    PATH = "mesh.s1.n1.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N1P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS1N1P1SampleFinished

    async def __call__(self) -> MeshS1N1P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s1.n1.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS1N1P1ArmFinished:
    """`mesh.s1.n1.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N1P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s1.n1.p1.arm`, uid 70.

    Returns one of:
      - `MeshS1N1P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N1_P1_ARM
    PATH = "mesh.s1.n1.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS1N1P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS1N1P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS1N1P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s1.n1.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS1N1P1HoldFinished:
    """`mesh.s1.n1.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N1P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s1.n1.p1.hold`, uid 71.

    Returns one of:
      - `MeshS1N1P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N1_P1_HOLD
    PATH = "mesh.s1.n1.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N1P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS1N1P1HoldFinished

    async def __call__(self) -> MeshS1N1P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s1.n1.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS1N1P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s1.n1.p1.quench`, uid 72.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S1_N1_P1_QUENCH
    PATH = "mesh.s1.n1.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s1.n1.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS1N1P2SampleFinished:
    """`mesh.s1.n1.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N1P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s1.n1.p2.sample`, uid 77.

    Returns one of:
      - `MeshS1N1P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N1_P2_SAMPLE
    PATH = "mesh.s1.n1.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N1P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS1N1P2SampleFinished

    async def __call__(self) -> MeshS1N1P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s1.n1.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS1N1P2ArmFinished:
    """`mesh.s1.n1.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N1P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s1.n1.p2.arm`, uid 74.

    Returns one of:
      - `MeshS1N1P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N1_P2_ARM
    PATH = "mesh.s1.n1.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS1N1P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS1N1P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS1N1P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s1.n1.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS1N1P2HoldFinished:
    """`mesh.s1.n1.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N1P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s1.n1.p2.hold`, uid 75.

    Returns one of:
      - `MeshS1N1P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N1_P2_HOLD
    PATH = "mesh.s1.n1.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N1P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS1N1P2HoldFinished

    async def __call__(self) -> MeshS1N1P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s1.n1.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS1N1P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s1.n1.p2.quench`, uid 76.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S1_N1_P2_QUENCH
    PATH = "mesh.s1.n1.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s1.n1.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS1N2P0SampleFinished:
    """`mesh.s1.n2.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N2P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s1.n2.p0.sample`, uid 81.

    Returns one of:
      - `MeshS1N2P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N2_P0_SAMPLE
    PATH = "mesh.s1.n2.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N2P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS1N2P0SampleFinished

    async def __call__(self) -> MeshS1N2P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s1.n2.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS1N2P0ArmFinished:
    """`mesh.s1.n2.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N2P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s1.n2.p0.arm`, uid 78.

    Returns one of:
      - `MeshS1N2P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N2_P0_ARM
    PATH = "mesh.s1.n2.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS1N2P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS1N2P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS1N2P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s1.n2.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS1N2P0HoldFinished:
    """`mesh.s1.n2.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N2P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s1.n2.p0.hold`, uid 79.

    Returns one of:
      - `MeshS1N2P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N2_P0_HOLD
    PATH = "mesh.s1.n2.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N2P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS1N2P0HoldFinished

    async def __call__(self) -> MeshS1N2P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s1.n2.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS1N2P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s1.n2.p0.quench`, uid 80.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S1_N2_P0_QUENCH
    PATH = "mesh.s1.n2.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s1.n2.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS1N2P1SampleFinished:
    """`mesh.s1.n2.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N2P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s1.n2.p1.sample`, uid 85.

    Returns one of:
      - `MeshS1N2P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N2_P1_SAMPLE
    PATH = "mesh.s1.n2.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N2P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS1N2P1SampleFinished

    async def __call__(self) -> MeshS1N2P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s1.n2.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS1N2P1ArmFinished:
    """`mesh.s1.n2.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N2P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s1.n2.p1.arm`, uid 82.

    Returns one of:
      - `MeshS1N2P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N2_P1_ARM
    PATH = "mesh.s1.n2.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS1N2P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS1N2P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS1N2P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s1.n2.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS1N2P1HoldFinished:
    """`mesh.s1.n2.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N2P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s1.n2.p1.hold`, uid 83.

    Returns one of:
      - `MeshS1N2P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N2_P1_HOLD
    PATH = "mesh.s1.n2.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N2P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS1N2P1HoldFinished

    async def __call__(self) -> MeshS1N2P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s1.n2.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS1N2P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s1.n2.p1.quench`, uid 84.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S1_N2_P1_QUENCH
    PATH = "mesh.s1.n2.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s1.n2.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS1N2P2SampleFinished:
    """`mesh.s1.n2.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N2P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s1.n2.p2.sample`, uid 89.

    Returns one of:
      - `MeshS1N2P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N2_P2_SAMPLE
    PATH = "mesh.s1.n2.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N2P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS1N2P2SampleFinished

    async def __call__(self) -> MeshS1N2P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s1.n2.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS1N2P2ArmFinished:
    """`mesh.s1.n2.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N2P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s1.n2.p2.arm`, uid 86.

    Returns one of:
      - `MeshS1N2P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N2_P2_ARM
    PATH = "mesh.s1.n2.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS1N2P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS1N2P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS1N2P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s1.n2.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS1N2P2HoldFinished:
    """`mesh.s1.n2.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N2P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s1.n2.p2.hold`, uid 87.

    Returns one of:
      - `MeshS1N2P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N2_P2_HOLD
    PATH = "mesh.s1.n2.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N2P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS1N2P2HoldFinished

    async def __call__(self) -> MeshS1N2P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s1.n2.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS1N2P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s1.n2.p2.quench`, uid 88.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S1_N2_P2_QUENCH
    PATH = "mesh.s1.n2.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s1.n2.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS1N3P0SampleFinished:
    """`mesh.s1.n3.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N3P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s1.n3.p0.sample`, uid 93.

    Returns one of:
      - `MeshS1N3P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N3_P0_SAMPLE
    PATH = "mesh.s1.n3.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N3P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS1N3P0SampleFinished

    async def __call__(self) -> MeshS1N3P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s1.n3.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS1N3P0ArmFinished:
    """`mesh.s1.n3.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N3P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s1.n3.p0.arm`, uid 90.

    Returns one of:
      - `MeshS1N3P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N3_P0_ARM
    PATH = "mesh.s1.n3.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS1N3P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS1N3P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS1N3P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s1.n3.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS1N3P0HoldFinished:
    """`mesh.s1.n3.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N3P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s1.n3.p0.hold`, uid 91.

    Returns one of:
      - `MeshS1N3P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N3_P0_HOLD
    PATH = "mesh.s1.n3.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N3P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS1N3P0HoldFinished

    async def __call__(self) -> MeshS1N3P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s1.n3.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS1N3P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s1.n3.p0.quench`, uid 92.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S1_N3_P0_QUENCH
    PATH = "mesh.s1.n3.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s1.n3.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS1N3P1SampleFinished:
    """`mesh.s1.n3.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N3P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s1.n3.p1.sample`, uid 97.

    Returns one of:
      - `MeshS1N3P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N3_P1_SAMPLE
    PATH = "mesh.s1.n3.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N3P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS1N3P1SampleFinished

    async def __call__(self) -> MeshS1N3P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s1.n3.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS1N3P1ArmFinished:
    """`mesh.s1.n3.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N3P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s1.n3.p1.arm`, uid 94.

    Returns one of:
      - `MeshS1N3P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N3_P1_ARM
    PATH = "mesh.s1.n3.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS1N3P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS1N3P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS1N3P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s1.n3.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS1N3P1HoldFinished:
    """`mesh.s1.n3.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N3P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s1.n3.p1.hold`, uid 95.

    Returns one of:
      - `MeshS1N3P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N3_P1_HOLD
    PATH = "mesh.s1.n3.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N3P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS1N3P1HoldFinished

    async def __call__(self) -> MeshS1N3P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s1.n3.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS1N3P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s1.n3.p1.quench`, uid 96.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S1_N3_P1_QUENCH
    PATH = "mesh.s1.n3.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s1.n3.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS1N3P2SampleFinished:
    """`mesh.s1.n3.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N3P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s1.n3.p2.sample`, uid 101.

    Returns one of:
      - `MeshS1N3P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N3_P2_SAMPLE
    PATH = "mesh.s1.n3.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N3P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS1N3P2SampleFinished

    async def __call__(self) -> MeshS1N3P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s1.n3.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS1N3P2ArmFinished:
    """`mesh.s1.n3.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N3P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s1.n3.p2.arm`, uid 98.

    Returns one of:
      - `MeshS1N3P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N3_P2_ARM
    PATH = "mesh.s1.n3.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS1N3P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS1N3P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS1N3P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s1.n3.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS1N3P2HoldFinished:
    """`mesh.s1.n3.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS1N3P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s1.n3.p2.hold`, uid 99.

    Returns one of:
      - `MeshS1N3P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S1_N3_P2_HOLD
    PATH = "mesh.s1.n3.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS1N3P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS1N3P2HoldFinished

    async def __call__(self) -> MeshS1N3P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s1.n3.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS1N3P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s1.n3.p2.quench`, uid 100.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S1_N3_P2_QUENCH
    PATH = "mesh.s1.n3.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s1.n3.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS2N0P0SampleFinished:
    """`mesh.s2.n0.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N0P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s2.n0.p0.sample`, uid 105.

    Returns one of:
      - `MeshS2N0P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N0_P0_SAMPLE
    PATH = "mesh.s2.n0.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N0P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS2N0P0SampleFinished

    async def __call__(self) -> MeshS2N0P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s2.n0.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS2N0P0ArmFinished:
    """`mesh.s2.n0.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N0P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s2.n0.p0.arm`, uid 102.

    Returns one of:
      - `MeshS2N0P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N0_P0_ARM
    PATH = "mesh.s2.n0.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS2N0P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS2N0P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS2N0P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s2.n0.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS2N0P0HoldFinished:
    """`mesh.s2.n0.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N0P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s2.n0.p0.hold`, uid 103.

    Returns one of:
      - `MeshS2N0P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N0_P0_HOLD
    PATH = "mesh.s2.n0.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N0P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS2N0P0HoldFinished

    async def __call__(self) -> MeshS2N0P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s2.n0.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS2N0P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s2.n0.p0.quench`, uid 104.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S2_N0_P0_QUENCH
    PATH = "mesh.s2.n0.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s2.n0.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS2N0P1SampleFinished:
    """`mesh.s2.n0.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N0P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s2.n0.p1.sample`, uid 109.

    Returns one of:
      - `MeshS2N0P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N0_P1_SAMPLE
    PATH = "mesh.s2.n0.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N0P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS2N0P1SampleFinished

    async def __call__(self) -> MeshS2N0P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s2.n0.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS2N0P1ArmFinished:
    """`mesh.s2.n0.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N0P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s2.n0.p1.arm`, uid 106.

    Returns one of:
      - `MeshS2N0P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N0_P1_ARM
    PATH = "mesh.s2.n0.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS2N0P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS2N0P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS2N0P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s2.n0.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS2N0P1HoldFinished:
    """`mesh.s2.n0.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N0P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s2.n0.p1.hold`, uid 107.

    Returns one of:
      - `MeshS2N0P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N0_P1_HOLD
    PATH = "mesh.s2.n0.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N0P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS2N0P1HoldFinished

    async def __call__(self) -> MeshS2N0P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s2.n0.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS2N0P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s2.n0.p1.quench`, uid 108.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S2_N0_P1_QUENCH
    PATH = "mesh.s2.n0.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s2.n0.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS2N0P2SampleFinished:
    """`mesh.s2.n0.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N0P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s2.n0.p2.sample`, uid 113.

    Returns one of:
      - `MeshS2N0P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N0_P2_SAMPLE
    PATH = "mesh.s2.n0.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N0P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS2N0P2SampleFinished

    async def __call__(self) -> MeshS2N0P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s2.n0.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS2N0P2ArmFinished:
    """`mesh.s2.n0.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N0P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s2.n0.p2.arm`, uid 110.

    Returns one of:
      - `MeshS2N0P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N0_P2_ARM
    PATH = "mesh.s2.n0.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS2N0P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS2N0P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS2N0P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s2.n0.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS2N0P2HoldFinished:
    """`mesh.s2.n0.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N0P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s2.n0.p2.hold`, uid 111.

    Returns one of:
      - `MeshS2N0P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N0_P2_HOLD
    PATH = "mesh.s2.n0.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N0P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS2N0P2HoldFinished

    async def __call__(self) -> MeshS2N0P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s2.n0.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS2N0P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s2.n0.p2.quench`, uid 112.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S2_N0_P2_QUENCH
    PATH = "mesh.s2.n0.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s2.n0.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS2N1P0SampleFinished:
    """`mesh.s2.n1.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N1P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s2.n1.p0.sample`, uid 117.

    Returns one of:
      - `MeshS2N1P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N1_P0_SAMPLE
    PATH = "mesh.s2.n1.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N1P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS2N1P0SampleFinished

    async def __call__(self) -> MeshS2N1P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s2.n1.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS2N1P0ArmFinished:
    """`mesh.s2.n1.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N1P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s2.n1.p0.arm`, uid 114.

    Returns one of:
      - `MeshS2N1P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N1_P0_ARM
    PATH = "mesh.s2.n1.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS2N1P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS2N1P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS2N1P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s2.n1.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS2N1P0HoldFinished:
    """`mesh.s2.n1.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N1P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s2.n1.p0.hold`, uid 115.

    Returns one of:
      - `MeshS2N1P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N1_P0_HOLD
    PATH = "mesh.s2.n1.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N1P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS2N1P0HoldFinished

    async def __call__(self) -> MeshS2N1P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s2.n1.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS2N1P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s2.n1.p0.quench`, uid 116.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S2_N1_P0_QUENCH
    PATH = "mesh.s2.n1.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s2.n1.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS2N1P1SampleFinished:
    """`mesh.s2.n1.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N1P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s2.n1.p1.sample`, uid 121.

    Returns one of:
      - `MeshS2N1P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N1_P1_SAMPLE
    PATH = "mesh.s2.n1.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N1P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS2N1P1SampleFinished

    async def __call__(self) -> MeshS2N1P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s2.n1.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS2N1P1ArmFinished:
    """`mesh.s2.n1.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N1P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s2.n1.p1.arm`, uid 118.

    Returns one of:
      - `MeshS2N1P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N1_P1_ARM
    PATH = "mesh.s2.n1.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS2N1P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS2N1P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS2N1P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s2.n1.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS2N1P1HoldFinished:
    """`mesh.s2.n1.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N1P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s2.n1.p1.hold`, uid 119.

    Returns one of:
      - `MeshS2N1P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N1_P1_HOLD
    PATH = "mesh.s2.n1.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N1P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS2N1P1HoldFinished

    async def __call__(self) -> MeshS2N1P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s2.n1.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS2N1P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s2.n1.p1.quench`, uid 120.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S2_N1_P1_QUENCH
    PATH = "mesh.s2.n1.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s2.n1.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS2N1P2SampleFinished:
    """`mesh.s2.n1.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N1P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s2.n1.p2.sample`, uid 125.

    Returns one of:
      - `MeshS2N1P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N1_P2_SAMPLE
    PATH = "mesh.s2.n1.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N1P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS2N1P2SampleFinished

    async def __call__(self) -> MeshS2N1P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s2.n1.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS2N1P2ArmFinished:
    """`mesh.s2.n1.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N1P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s2.n1.p2.arm`, uid 122.

    Returns one of:
      - `MeshS2N1P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N1_P2_ARM
    PATH = "mesh.s2.n1.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS2N1P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS2N1P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS2N1P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s2.n1.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS2N1P2HoldFinished:
    """`mesh.s2.n1.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N1P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s2.n1.p2.hold`, uid 123.

    Returns one of:
      - `MeshS2N1P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N1_P2_HOLD
    PATH = "mesh.s2.n1.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N1P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS2N1P2HoldFinished

    async def __call__(self) -> MeshS2N1P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s2.n1.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS2N1P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s2.n1.p2.quench`, uid 124.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S2_N1_P2_QUENCH
    PATH = "mesh.s2.n1.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s2.n1.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS2N2P0SampleFinished:
    """`mesh.s2.n2.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N2P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s2.n2.p0.sample`, uid 129.

    Returns one of:
      - `MeshS2N2P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N2_P0_SAMPLE
    PATH = "mesh.s2.n2.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N2P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS2N2P0SampleFinished

    async def __call__(self) -> MeshS2N2P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s2.n2.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS2N2P0ArmFinished:
    """`mesh.s2.n2.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N2P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s2.n2.p0.arm`, uid 126.

    Returns one of:
      - `MeshS2N2P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N2_P0_ARM
    PATH = "mesh.s2.n2.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS2N2P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS2N2P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS2N2P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s2.n2.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS2N2P0HoldFinished:
    """`mesh.s2.n2.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N2P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s2.n2.p0.hold`, uid 127.

    Returns one of:
      - `MeshS2N2P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N2_P0_HOLD
    PATH = "mesh.s2.n2.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N2P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS2N2P0HoldFinished

    async def __call__(self) -> MeshS2N2P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s2.n2.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS2N2P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s2.n2.p0.quench`, uid 128.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S2_N2_P0_QUENCH
    PATH = "mesh.s2.n2.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s2.n2.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS2N2P1SampleFinished:
    """`mesh.s2.n2.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N2P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s2.n2.p1.sample`, uid 133.

    Returns one of:
      - `MeshS2N2P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N2_P1_SAMPLE
    PATH = "mesh.s2.n2.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N2P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS2N2P1SampleFinished

    async def __call__(self) -> MeshS2N2P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s2.n2.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS2N2P1ArmFinished:
    """`mesh.s2.n2.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N2P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s2.n2.p1.arm`, uid 130.

    Returns one of:
      - `MeshS2N2P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N2_P1_ARM
    PATH = "mesh.s2.n2.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS2N2P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS2N2P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS2N2P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s2.n2.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS2N2P1HoldFinished:
    """`mesh.s2.n2.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N2P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s2.n2.p1.hold`, uid 131.

    Returns one of:
      - `MeshS2N2P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N2_P1_HOLD
    PATH = "mesh.s2.n2.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N2P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS2N2P1HoldFinished

    async def __call__(self) -> MeshS2N2P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s2.n2.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS2N2P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s2.n2.p1.quench`, uid 132.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S2_N2_P1_QUENCH
    PATH = "mesh.s2.n2.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s2.n2.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS2N2P2SampleFinished:
    """`mesh.s2.n2.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N2P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s2.n2.p2.sample`, uid 137.

    Returns one of:
      - `MeshS2N2P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N2_P2_SAMPLE
    PATH = "mesh.s2.n2.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N2P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS2N2P2SampleFinished

    async def __call__(self) -> MeshS2N2P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s2.n2.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS2N2P2ArmFinished:
    """`mesh.s2.n2.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N2P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s2.n2.p2.arm`, uid 134.

    Returns one of:
      - `MeshS2N2P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N2_P2_ARM
    PATH = "mesh.s2.n2.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS2N2P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS2N2P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS2N2P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s2.n2.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS2N2P2HoldFinished:
    """`mesh.s2.n2.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N2P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s2.n2.p2.hold`, uid 135.

    Returns one of:
      - `MeshS2N2P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N2_P2_HOLD
    PATH = "mesh.s2.n2.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N2P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS2N2P2HoldFinished

    async def __call__(self) -> MeshS2N2P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s2.n2.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS2N2P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s2.n2.p2.quench`, uid 136.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S2_N2_P2_QUENCH
    PATH = "mesh.s2.n2.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s2.n2.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS2N3P0SampleFinished:
    """`mesh.s2.n3.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N3P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s2.n3.p0.sample`, uid 141.

    Returns one of:
      - `MeshS2N3P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N3_P0_SAMPLE
    PATH = "mesh.s2.n3.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N3P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS2N3P0SampleFinished

    async def __call__(self) -> MeshS2N3P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s2.n3.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS2N3P0ArmFinished:
    """`mesh.s2.n3.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N3P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s2.n3.p0.arm`, uid 138.

    Returns one of:
      - `MeshS2N3P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N3_P0_ARM
    PATH = "mesh.s2.n3.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS2N3P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS2N3P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS2N3P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s2.n3.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS2N3P0HoldFinished:
    """`mesh.s2.n3.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N3P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s2.n3.p0.hold`, uid 139.

    Returns one of:
      - `MeshS2N3P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N3_P0_HOLD
    PATH = "mesh.s2.n3.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N3P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS2N3P0HoldFinished

    async def __call__(self) -> MeshS2N3P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s2.n3.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS2N3P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s2.n3.p0.quench`, uid 140.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S2_N3_P0_QUENCH
    PATH = "mesh.s2.n3.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s2.n3.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS2N3P1SampleFinished:
    """`mesh.s2.n3.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N3P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s2.n3.p1.sample`, uid 145.

    Returns one of:
      - `MeshS2N3P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N3_P1_SAMPLE
    PATH = "mesh.s2.n3.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N3P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS2N3P1SampleFinished

    async def __call__(self) -> MeshS2N3P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s2.n3.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS2N3P1ArmFinished:
    """`mesh.s2.n3.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N3P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s2.n3.p1.arm`, uid 142.

    Returns one of:
      - `MeshS2N3P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N3_P1_ARM
    PATH = "mesh.s2.n3.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS2N3P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS2N3P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS2N3P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s2.n3.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS2N3P1HoldFinished:
    """`mesh.s2.n3.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N3P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s2.n3.p1.hold`, uid 143.

    Returns one of:
      - `MeshS2N3P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N3_P1_HOLD
    PATH = "mesh.s2.n3.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N3P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS2N3P1HoldFinished

    async def __call__(self) -> MeshS2N3P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s2.n3.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS2N3P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s2.n3.p1.quench`, uid 144.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S2_N3_P1_QUENCH
    PATH = "mesh.s2.n3.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s2.n3.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS2N3P2SampleFinished:
    """`mesh.s2.n3.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N3P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s2.n3.p2.sample`, uid 149.

    Returns one of:
      - `MeshS2N3P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N3_P2_SAMPLE
    PATH = "mesh.s2.n3.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N3P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS2N3P2SampleFinished

    async def __call__(self) -> MeshS2N3P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s2.n3.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS2N3P2ArmFinished:
    """`mesh.s2.n3.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N3P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s2.n3.p2.arm`, uid 146.

    Returns one of:
      - `MeshS2N3P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N3_P2_ARM
    PATH = "mesh.s2.n3.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS2N3P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS2N3P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS2N3P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s2.n3.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS2N3P2HoldFinished:
    """`mesh.s2.n3.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS2N3P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s2.n3.p2.hold`, uid 147.

    Returns one of:
      - `MeshS2N3P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S2_N3_P2_HOLD
    PATH = "mesh.s2.n3.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS2N3P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS2N3P2HoldFinished

    async def __call__(self) -> MeshS2N3P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s2.n3.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS2N3P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s2.n3.p2.quench`, uid 148.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S2_N3_P2_QUENCH
    PATH = "mesh.s2.n3.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s2.n3.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS3N0P0SampleFinished:
    """`mesh.s3.n0.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N0P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s3.n0.p0.sample`, uid 153.

    Returns one of:
      - `MeshS3N0P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N0_P0_SAMPLE
    PATH = "mesh.s3.n0.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N0P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS3N0P0SampleFinished

    async def __call__(self) -> MeshS3N0P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s3.n0.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS3N0P0ArmFinished:
    """`mesh.s3.n0.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N0P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s3.n0.p0.arm`, uid 150.

    Returns one of:
      - `MeshS3N0P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N0_P0_ARM
    PATH = "mesh.s3.n0.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS3N0P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS3N0P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS3N0P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s3.n0.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS3N0P0HoldFinished:
    """`mesh.s3.n0.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N0P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s3.n0.p0.hold`, uid 151.

    Returns one of:
      - `MeshS3N0P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N0_P0_HOLD
    PATH = "mesh.s3.n0.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N0P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS3N0P0HoldFinished

    async def __call__(self) -> MeshS3N0P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s3.n0.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS3N0P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s3.n0.p0.quench`, uid 152.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S3_N0_P0_QUENCH
    PATH = "mesh.s3.n0.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s3.n0.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS3N0P1SampleFinished:
    """`mesh.s3.n0.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N0P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s3.n0.p1.sample`, uid 157.

    Returns one of:
      - `MeshS3N0P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N0_P1_SAMPLE
    PATH = "mesh.s3.n0.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N0P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS3N0P1SampleFinished

    async def __call__(self) -> MeshS3N0P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s3.n0.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS3N0P1ArmFinished:
    """`mesh.s3.n0.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N0P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s3.n0.p1.arm`, uid 154.

    Returns one of:
      - `MeshS3N0P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N0_P1_ARM
    PATH = "mesh.s3.n0.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS3N0P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS3N0P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS3N0P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s3.n0.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS3N0P1HoldFinished:
    """`mesh.s3.n0.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N0P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s3.n0.p1.hold`, uid 155.

    Returns one of:
      - `MeshS3N0P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N0_P1_HOLD
    PATH = "mesh.s3.n0.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N0P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS3N0P1HoldFinished

    async def __call__(self) -> MeshS3N0P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s3.n0.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS3N0P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s3.n0.p1.quench`, uid 156.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S3_N0_P1_QUENCH
    PATH = "mesh.s3.n0.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s3.n0.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS3N0P2SampleFinished:
    """`mesh.s3.n0.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N0P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s3.n0.p2.sample`, uid 161.

    Returns one of:
      - `MeshS3N0P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N0_P2_SAMPLE
    PATH = "mesh.s3.n0.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N0P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS3N0P2SampleFinished

    async def __call__(self) -> MeshS3N0P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s3.n0.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS3N0P2ArmFinished:
    """`mesh.s3.n0.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N0P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s3.n0.p2.arm`, uid 158.

    Returns one of:
      - `MeshS3N0P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N0_P2_ARM
    PATH = "mesh.s3.n0.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS3N0P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS3N0P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS3N0P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s3.n0.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS3N0P2HoldFinished:
    """`mesh.s3.n0.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N0P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s3.n0.p2.hold`, uid 159.

    Returns one of:
      - `MeshS3N0P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N0_P2_HOLD
    PATH = "mesh.s3.n0.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N0P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS3N0P2HoldFinished

    async def __call__(self) -> MeshS3N0P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s3.n0.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS3N0P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s3.n0.p2.quench`, uid 160.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S3_N0_P2_QUENCH
    PATH = "mesh.s3.n0.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s3.n0.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS3N1P0SampleFinished:
    """`mesh.s3.n1.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N1P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s3.n1.p0.sample`, uid 165.

    Returns one of:
      - `MeshS3N1P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N1_P0_SAMPLE
    PATH = "mesh.s3.n1.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N1P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS3N1P0SampleFinished

    async def __call__(self) -> MeshS3N1P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s3.n1.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS3N1P0ArmFinished:
    """`mesh.s3.n1.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N1P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s3.n1.p0.arm`, uid 162.

    Returns one of:
      - `MeshS3N1P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N1_P0_ARM
    PATH = "mesh.s3.n1.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS3N1P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS3N1P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS3N1P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s3.n1.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS3N1P0HoldFinished:
    """`mesh.s3.n1.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N1P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s3.n1.p0.hold`, uid 163.

    Returns one of:
      - `MeshS3N1P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N1_P0_HOLD
    PATH = "mesh.s3.n1.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N1P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS3N1P0HoldFinished

    async def __call__(self) -> MeshS3N1P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s3.n1.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS3N1P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s3.n1.p0.quench`, uid 164.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S3_N1_P0_QUENCH
    PATH = "mesh.s3.n1.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s3.n1.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS3N1P1SampleFinished:
    """`mesh.s3.n1.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N1P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s3.n1.p1.sample`, uid 169.

    Returns one of:
      - `MeshS3N1P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N1_P1_SAMPLE
    PATH = "mesh.s3.n1.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N1P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS3N1P1SampleFinished

    async def __call__(self) -> MeshS3N1P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s3.n1.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS3N1P1ArmFinished:
    """`mesh.s3.n1.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N1P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s3.n1.p1.arm`, uid 166.

    Returns one of:
      - `MeshS3N1P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N1_P1_ARM
    PATH = "mesh.s3.n1.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS3N1P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS3N1P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS3N1P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s3.n1.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS3N1P1HoldFinished:
    """`mesh.s3.n1.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N1P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s3.n1.p1.hold`, uid 167.

    Returns one of:
      - `MeshS3N1P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N1_P1_HOLD
    PATH = "mesh.s3.n1.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N1P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS3N1P1HoldFinished

    async def __call__(self) -> MeshS3N1P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s3.n1.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS3N1P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s3.n1.p1.quench`, uid 168.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S3_N1_P1_QUENCH
    PATH = "mesh.s3.n1.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s3.n1.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS3N1P2SampleFinished:
    """`mesh.s3.n1.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N1P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s3.n1.p2.sample`, uid 173.

    Returns one of:
      - `MeshS3N1P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N1_P2_SAMPLE
    PATH = "mesh.s3.n1.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N1P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS3N1P2SampleFinished

    async def __call__(self) -> MeshS3N1P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s3.n1.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS3N1P2ArmFinished:
    """`mesh.s3.n1.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N1P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s3.n1.p2.arm`, uid 170.

    Returns one of:
      - `MeshS3N1P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N1_P2_ARM
    PATH = "mesh.s3.n1.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS3N1P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS3N1P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS3N1P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s3.n1.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS3N1P2HoldFinished:
    """`mesh.s3.n1.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N1P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s3.n1.p2.hold`, uid 171.

    Returns one of:
      - `MeshS3N1P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N1_P2_HOLD
    PATH = "mesh.s3.n1.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N1P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS3N1P2HoldFinished

    async def __call__(self) -> MeshS3N1P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s3.n1.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS3N1P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s3.n1.p2.quench`, uid 172.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S3_N1_P2_QUENCH
    PATH = "mesh.s3.n1.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s3.n1.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS3N2P0SampleFinished:
    """`mesh.s3.n2.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N2P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s3.n2.p0.sample`, uid 177.

    Returns one of:
      - `MeshS3N2P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N2_P0_SAMPLE
    PATH = "mesh.s3.n2.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N2P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS3N2P0SampleFinished

    async def __call__(self) -> MeshS3N2P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s3.n2.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS3N2P0ArmFinished:
    """`mesh.s3.n2.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N2P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s3.n2.p0.arm`, uid 174.

    Returns one of:
      - `MeshS3N2P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N2_P0_ARM
    PATH = "mesh.s3.n2.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS3N2P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS3N2P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS3N2P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s3.n2.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS3N2P0HoldFinished:
    """`mesh.s3.n2.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N2P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s3.n2.p0.hold`, uid 175.

    Returns one of:
      - `MeshS3N2P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N2_P0_HOLD
    PATH = "mesh.s3.n2.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N2P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS3N2P0HoldFinished

    async def __call__(self) -> MeshS3N2P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s3.n2.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS3N2P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s3.n2.p0.quench`, uid 176.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S3_N2_P0_QUENCH
    PATH = "mesh.s3.n2.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s3.n2.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS3N2P1SampleFinished:
    """`mesh.s3.n2.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N2P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s3.n2.p1.sample`, uid 181.

    Returns one of:
      - `MeshS3N2P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N2_P1_SAMPLE
    PATH = "mesh.s3.n2.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N2P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS3N2P1SampleFinished

    async def __call__(self) -> MeshS3N2P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s3.n2.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS3N2P1ArmFinished:
    """`mesh.s3.n2.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N2P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s3.n2.p1.arm`, uid 178.

    Returns one of:
      - `MeshS3N2P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N2_P1_ARM
    PATH = "mesh.s3.n2.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS3N2P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS3N2P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS3N2P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s3.n2.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS3N2P1HoldFinished:
    """`mesh.s3.n2.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N2P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s3.n2.p1.hold`, uid 179.

    Returns one of:
      - `MeshS3N2P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N2_P1_HOLD
    PATH = "mesh.s3.n2.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N2P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS3N2P1HoldFinished

    async def __call__(self) -> MeshS3N2P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s3.n2.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS3N2P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s3.n2.p1.quench`, uid 180.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S3_N2_P1_QUENCH
    PATH = "mesh.s3.n2.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s3.n2.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS3N2P2SampleFinished:
    """`mesh.s3.n2.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N2P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s3.n2.p2.sample`, uid 185.

    Returns one of:
      - `MeshS3N2P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N2_P2_SAMPLE
    PATH = "mesh.s3.n2.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N2P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS3N2P2SampleFinished

    async def __call__(self) -> MeshS3N2P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s3.n2.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS3N2P2ArmFinished:
    """`mesh.s3.n2.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N2P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s3.n2.p2.arm`, uid 182.

    Returns one of:
      - `MeshS3N2P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N2_P2_ARM
    PATH = "mesh.s3.n2.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS3N2P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS3N2P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS3N2P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s3.n2.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS3N2P2HoldFinished:
    """`mesh.s3.n2.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N2P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s3.n2.p2.hold`, uid 183.

    Returns one of:
      - `MeshS3N2P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N2_P2_HOLD
    PATH = "mesh.s3.n2.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N2P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS3N2P2HoldFinished

    async def __call__(self) -> MeshS3N2P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s3.n2.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS3N2P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s3.n2.p2.quench`, uid 184.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S3_N2_P2_QUENCH
    PATH = "mesh.s3.n2.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s3.n2.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS3N3P0SampleFinished:
    """`mesh.s3.n3.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N3P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s3.n3.p0.sample`, uid 189.

    Returns one of:
      - `MeshS3N3P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N3_P0_SAMPLE
    PATH = "mesh.s3.n3.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N3P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS3N3P0SampleFinished

    async def __call__(self) -> MeshS3N3P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s3.n3.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS3N3P0ArmFinished:
    """`mesh.s3.n3.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N3P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s3.n3.p0.arm`, uid 186.

    Returns one of:
      - `MeshS3N3P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N3_P0_ARM
    PATH = "mesh.s3.n3.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS3N3P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS3N3P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS3N3P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s3.n3.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS3N3P0HoldFinished:
    """`mesh.s3.n3.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N3P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s3.n3.p0.hold`, uid 187.

    Returns one of:
      - `MeshS3N3P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N3_P0_HOLD
    PATH = "mesh.s3.n3.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N3P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS3N3P0HoldFinished

    async def __call__(self) -> MeshS3N3P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s3.n3.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS3N3P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s3.n3.p0.quench`, uid 188.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S3_N3_P0_QUENCH
    PATH = "mesh.s3.n3.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s3.n3.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS3N3P1SampleFinished:
    """`mesh.s3.n3.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N3P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s3.n3.p1.sample`, uid 193.

    Returns one of:
      - `MeshS3N3P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N3_P1_SAMPLE
    PATH = "mesh.s3.n3.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N3P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS3N3P1SampleFinished

    async def __call__(self) -> MeshS3N3P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s3.n3.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS3N3P1ArmFinished:
    """`mesh.s3.n3.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N3P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s3.n3.p1.arm`, uid 190.

    Returns one of:
      - `MeshS3N3P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N3_P1_ARM
    PATH = "mesh.s3.n3.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS3N3P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS3N3P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS3N3P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s3.n3.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS3N3P1HoldFinished:
    """`mesh.s3.n3.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N3P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s3.n3.p1.hold`, uid 191.

    Returns one of:
      - `MeshS3N3P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N3_P1_HOLD
    PATH = "mesh.s3.n3.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N3P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS3N3P1HoldFinished

    async def __call__(self) -> MeshS3N3P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s3.n3.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS3N3P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s3.n3.p1.quench`, uid 192.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S3_N3_P1_QUENCH
    PATH = "mesh.s3.n3.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s3.n3.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS3N3P2SampleFinished:
    """`mesh.s3.n3.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N3P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s3.n3.p2.sample`, uid 197.

    Returns one of:
      - `MeshS3N3P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N3_P2_SAMPLE
    PATH = "mesh.s3.n3.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N3P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS3N3P2SampleFinished

    async def __call__(self) -> MeshS3N3P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s3.n3.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS3N3P2ArmFinished:
    """`mesh.s3.n3.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N3P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s3.n3.p2.arm`, uid 194.

    Returns one of:
      - `MeshS3N3P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N3_P2_ARM
    PATH = "mesh.s3.n3.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS3N3P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS3N3P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS3N3P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s3.n3.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS3N3P2HoldFinished:
    """`mesh.s3.n3.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS3N3P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s3.n3.p2.hold`, uid 195.

    Returns one of:
      - `MeshS3N3P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S3_N3_P2_HOLD
    PATH = "mesh.s3.n3.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS3N3P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS3N3P2HoldFinished

    async def __call__(self) -> MeshS3N3P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s3.n3.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS3N3P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s3.n3.p2.quench`, uid 196.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S3_N3_P2_QUENCH
    PATH = "mesh.s3.n3.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s3.n3.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS4N0P0SampleFinished:
    """`mesh.s4.n0.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N0P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s4.n0.p0.sample`, uid 201.

    Returns one of:
      - `MeshS4N0P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N0_P0_SAMPLE
    PATH = "mesh.s4.n0.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N0P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS4N0P0SampleFinished

    async def __call__(self) -> MeshS4N0P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s4.n0.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS4N0P0ArmFinished:
    """`mesh.s4.n0.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N0P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s4.n0.p0.arm`, uid 198.

    Returns one of:
      - `MeshS4N0P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N0_P0_ARM
    PATH = "mesh.s4.n0.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS4N0P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS4N0P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS4N0P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s4.n0.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS4N0P0HoldFinished:
    """`mesh.s4.n0.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N0P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s4.n0.p0.hold`, uid 199.

    Returns one of:
      - `MeshS4N0P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N0_P0_HOLD
    PATH = "mesh.s4.n0.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N0P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS4N0P0HoldFinished

    async def __call__(self) -> MeshS4N0P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s4.n0.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS4N0P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s4.n0.p0.quench`, uid 200.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S4_N0_P0_QUENCH
    PATH = "mesh.s4.n0.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s4.n0.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS4N0P1SampleFinished:
    """`mesh.s4.n0.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N0P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s4.n0.p1.sample`, uid 205.

    Returns one of:
      - `MeshS4N0P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N0_P1_SAMPLE
    PATH = "mesh.s4.n0.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N0P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS4N0P1SampleFinished

    async def __call__(self) -> MeshS4N0P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s4.n0.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS4N0P1ArmFinished:
    """`mesh.s4.n0.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N0P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s4.n0.p1.arm`, uid 202.

    Returns one of:
      - `MeshS4N0P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N0_P1_ARM
    PATH = "mesh.s4.n0.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS4N0P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS4N0P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS4N0P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s4.n0.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS4N0P1HoldFinished:
    """`mesh.s4.n0.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N0P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s4.n0.p1.hold`, uid 203.

    Returns one of:
      - `MeshS4N0P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N0_P1_HOLD
    PATH = "mesh.s4.n0.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N0P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS4N0P1HoldFinished

    async def __call__(self) -> MeshS4N0P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s4.n0.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS4N0P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s4.n0.p1.quench`, uid 204.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S4_N0_P1_QUENCH
    PATH = "mesh.s4.n0.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s4.n0.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS4N0P2SampleFinished:
    """`mesh.s4.n0.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N0P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s4.n0.p2.sample`, uid 209.

    Returns one of:
      - `MeshS4N0P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N0_P2_SAMPLE
    PATH = "mesh.s4.n0.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N0P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS4N0P2SampleFinished

    async def __call__(self) -> MeshS4N0P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s4.n0.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS4N0P2ArmFinished:
    """`mesh.s4.n0.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N0P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s4.n0.p2.arm`, uid 206.

    Returns one of:
      - `MeshS4N0P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N0_P2_ARM
    PATH = "mesh.s4.n0.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS4N0P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS4N0P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS4N0P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s4.n0.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS4N0P2HoldFinished:
    """`mesh.s4.n0.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N0P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s4.n0.p2.hold`, uid 207.

    Returns one of:
      - `MeshS4N0P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N0_P2_HOLD
    PATH = "mesh.s4.n0.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N0P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS4N0P2HoldFinished

    async def __call__(self) -> MeshS4N0P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s4.n0.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS4N0P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s4.n0.p2.quench`, uid 208.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S4_N0_P2_QUENCH
    PATH = "mesh.s4.n0.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s4.n0.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS4N1P0SampleFinished:
    """`mesh.s4.n1.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N1P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s4.n1.p0.sample`, uid 213.

    Returns one of:
      - `MeshS4N1P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N1_P0_SAMPLE
    PATH = "mesh.s4.n1.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N1P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS4N1P0SampleFinished

    async def __call__(self) -> MeshS4N1P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s4.n1.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS4N1P0ArmFinished:
    """`mesh.s4.n1.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N1P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s4.n1.p0.arm`, uid 210.

    Returns one of:
      - `MeshS4N1P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N1_P0_ARM
    PATH = "mesh.s4.n1.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS4N1P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS4N1P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS4N1P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s4.n1.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS4N1P0HoldFinished:
    """`mesh.s4.n1.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N1P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s4.n1.p0.hold`, uid 211.

    Returns one of:
      - `MeshS4N1P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N1_P0_HOLD
    PATH = "mesh.s4.n1.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N1P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS4N1P0HoldFinished

    async def __call__(self) -> MeshS4N1P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s4.n1.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS4N1P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s4.n1.p0.quench`, uid 212.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S4_N1_P0_QUENCH
    PATH = "mesh.s4.n1.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s4.n1.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS4N1P1SampleFinished:
    """`mesh.s4.n1.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N1P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s4.n1.p1.sample`, uid 217.

    Returns one of:
      - `MeshS4N1P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N1_P1_SAMPLE
    PATH = "mesh.s4.n1.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N1P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS4N1P1SampleFinished

    async def __call__(self) -> MeshS4N1P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s4.n1.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS4N1P1ArmFinished:
    """`mesh.s4.n1.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N1P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s4.n1.p1.arm`, uid 214.

    Returns one of:
      - `MeshS4N1P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N1_P1_ARM
    PATH = "mesh.s4.n1.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS4N1P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS4N1P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS4N1P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s4.n1.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS4N1P1HoldFinished:
    """`mesh.s4.n1.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N1P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s4.n1.p1.hold`, uid 215.

    Returns one of:
      - `MeshS4N1P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N1_P1_HOLD
    PATH = "mesh.s4.n1.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N1P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS4N1P1HoldFinished

    async def __call__(self) -> MeshS4N1P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s4.n1.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS4N1P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s4.n1.p1.quench`, uid 216.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S4_N1_P1_QUENCH
    PATH = "mesh.s4.n1.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s4.n1.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS4N1P2SampleFinished:
    """`mesh.s4.n1.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N1P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s4.n1.p2.sample`, uid 221.

    Returns one of:
      - `MeshS4N1P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N1_P2_SAMPLE
    PATH = "mesh.s4.n1.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N1P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS4N1P2SampleFinished

    async def __call__(self) -> MeshS4N1P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s4.n1.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS4N1P2ArmFinished:
    """`mesh.s4.n1.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N1P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s4.n1.p2.arm`, uid 218.

    Returns one of:
      - `MeshS4N1P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N1_P2_ARM
    PATH = "mesh.s4.n1.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS4N1P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS4N1P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS4N1P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s4.n1.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS4N1P2HoldFinished:
    """`mesh.s4.n1.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N1P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s4.n1.p2.hold`, uid 219.

    Returns one of:
      - `MeshS4N1P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N1_P2_HOLD
    PATH = "mesh.s4.n1.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N1P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS4N1P2HoldFinished

    async def __call__(self) -> MeshS4N1P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s4.n1.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS4N1P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s4.n1.p2.quench`, uid 220.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S4_N1_P2_QUENCH
    PATH = "mesh.s4.n1.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s4.n1.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS4N2P0SampleFinished:
    """`mesh.s4.n2.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N2P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s4.n2.p0.sample`, uid 225.

    Returns one of:
      - `MeshS4N2P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N2_P0_SAMPLE
    PATH = "mesh.s4.n2.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N2P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS4N2P0SampleFinished

    async def __call__(self) -> MeshS4N2P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s4.n2.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS4N2P0ArmFinished:
    """`mesh.s4.n2.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N2P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s4.n2.p0.arm`, uid 222.

    Returns one of:
      - `MeshS4N2P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N2_P0_ARM
    PATH = "mesh.s4.n2.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS4N2P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS4N2P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS4N2P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s4.n2.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS4N2P0HoldFinished:
    """`mesh.s4.n2.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N2P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s4.n2.p0.hold`, uid 223.

    Returns one of:
      - `MeshS4N2P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N2_P0_HOLD
    PATH = "mesh.s4.n2.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N2P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS4N2P0HoldFinished

    async def __call__(self) -> MeshS4N2P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s4.n2.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS4N2P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s4.n2.p0.quench`, uid 224.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S4_N2_P0_QUENCH
    PATH = "mesh.s4.n2.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s4.n2.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS4N2P1SampleFinished:
    """`mesh.s4.n2.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N2P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s4.n2.p1.sample`, uid 229.

    Returns one of:
      - `MeshS4N2P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N2_P1_SAMPLE
    PATH = "mesh.s4.n2.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N2P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS4N2P1SampleFinished

    async def __call__(self) -> MeshS4N2P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s4.n2.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS4N2P1ArmFinished:
    """`mesh.s4.n2.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N2P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s4.n2.p1.arm`, uid 226.

    Returns one of:
      - `MeshS4N2P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N2_P1_ARM
    PATH = "mesh.s4.n2.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS4N2P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS4N2P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS4N2P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s4.n2.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS4N2P1HoldFinished:
    """`mesh.s4.n2.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N2P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s4.n2.p1.hold`, uid 227.

    Returns one of:
      - `MeshS4N2P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N2_P1_HOLD
    PATH = "mesh.s4.n2.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N2P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS4N2P1HoldFinished

    async def __call__(self) -> MeshS4N2P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s4.n2.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS4N2P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s4.n2.p1.quench`, uid 228.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S4_N2_P1_QUENCH
    PATH = "mesh.s4.n2.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s4.n2.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS4N2P2SampleFinished:
    """`mesh.s4.n2.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N2P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s4.n2.p2.sample`, uid 233.

    Returns one of:
      - `MeshS4N2P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N2_P2_SAMPLE
    PATH = "mesh.s4.n2.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N2P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS4N2P2SampleFinished

    async def __call__(self) -> MeshS4N2P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s4.n2.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS4N2P2ArmFinished:
    """`mesh.s4.n2.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N2P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s4.n2.p2.arm`, uid 230.

    Returns one of:
      - `MeshS4N2P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N2_P2_ARM
    PATH = "mesh.s4.n2.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS4N2P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS4N2P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS4N2P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s4.n2.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS4N2P2HoldFinished:
    """`mesh.s4.n2.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N2P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s4.n2.p2.hold`, uid 231.

    Returns one of:
      - `MeshS4N2P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N2_P2_HOLD
    PATH = "mesh.s4.n2.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N2P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS4N2P2HoldFinished

    async def __call__(self) -> MeshS4N2P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s4.n2.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS4N2P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s4.n2.p2.quench`, uid 232.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S4_N2_P2_QUENCH
    PATH = "mesh.s4.n2.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s4.n2.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS4N3P0SampleFinished:
    """`mesh.s4.n3.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N3P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s4.n3.p0.sample`, uid 237.

    Returns one of:
      - `MeshS4N3P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N3_P0_SAMPLE
    PATH = "mesh.s4.n3.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N3P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS4N3P0SampleFinished

    async def __call__(self) -> MeshS4N3P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s4.n3.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS4N3P0ArmFinished:
    """`mesh.s4.n3.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N3P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s4.n3.p0.arm`, uid 234.

    Returns one of:
      - `MeshS4N3P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N3_P0_ARM
    PATH = "mesh.s4.n3.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS4N3P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS4N3P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS4N3P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s4.n3.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS4N3P0HoldFinished:
    """`mesh.s4.n3.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N3P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s4.n3.p0.hold`, uid 235.

    Returns one of:
      - `MeshS4N3P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N3_P0_HOLD
    PATH = "mesh.s4.n3.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N3P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS4N3P0HoldFinished

    async def __call__(self) -> MeshS4N3P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s4.n3.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS4N3P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s4.n3.p0.quench`, uid 236.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S4_N3_P0_QUENCH
    PATH = "mesh.s4.n3.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s4.n3.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS4N3P1SampleFinished:
    """`mesh.s4.n3.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N3P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s4.n3.p1.sample`, uid 241.

    Returns one of:
      - `MeshS4N3P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N3_P1_SAMPLE
    PATH = "mesh.s4.n3.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N3P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS4N3P1SampleFinished

    async def __call__(self) -> MeshS4N3P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s4.n3.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS4N3P1ArmFinished:
    """`mesh.s4.n3.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N3P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s4.n3.p1.arm`, uid 238.

    Returns one of:
      - `MeshS4N3P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N3_P1_ARM
    PATH = "mesh.s4.n3.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS4N3P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS4N3P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS4N3P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s4.n3.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS4N3P1HoldFinished:
    """`mesh.s4.n3.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N3P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s4.n3.p1.hold`, uid 239.

    Returns one of:
      - `MeshS4N3P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N3_P1_HOLD
    PATH = "mesh.s4.n3.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N3P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS4N3P1HoldFinished

    async def __call__(self) -> MeshS4N3P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s4.n3.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS4N3P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s4.n3.p1.quench`, uid 240.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S4_N3_P1_QUENCH
    PATH = "mesh.s4.n3.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s4.n3.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS4N3P2SampleFinished:
    """`mesh.s4.n3.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N3P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s4.n3.p2.sample`, uid 245.

    Returns one of:
      - `MeshS4N3P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N3_P2_SAMPLE
    PATH = "mesh.s4.n3.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N3P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS4N3P2SampleFinished

    async def __call__(self) -> MeshS4N3P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s4.n3.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS4N3P2ArmFinished:
    """`mesh.s4.n3.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N3P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s4.n3.p2.arm`, uid 242.

    Returns one of:
      - `MeshS4N3P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N3_P2_ARM
    PATH = "mesh.s4.n3.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS4N3P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS4N3P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS4N3P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s4.n3.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS4N3P2HoldFinished:
    """`mesh.s4.n3.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS4N3P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s4.n3.p2.hold`, uid 243.

    Returns one of:
      - `MeshS4N3P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S4_N3_P2_HOLD
    PATH = "mesh.s4.n3.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS4N3P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS4N3P2HoldFinished

    async def __call__(self) -> MeshS4N3P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s4.n3.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS4N3P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s4.n3.p2.quench`, uid 244.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S4_N3_P2_QUENCH
    PATH = "mesh.s4.n3.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s4.n3.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS5N0P0SampleFinished:
    """`mesh.s5.n0.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N0P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s5.n0.p0.sample`, uid 249.

    Returns one of:
      - `MeshS5N0P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N0_P0_SAMPLE
    PATH = "mesh.s5.n0.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N0P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS5N0P0SampleFinished

    async def __call__(self) -> MeshS5N0P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s5.n0.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS5N0P0ArmFinished:
    """`mesh.s5.n0.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N0P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s5.n0.p0.arm`, uid 246.

    Returns one of:
      - `MeshS5N0P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N0_P0_ARM
    PATH = "mesh.s5.n0.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS5N0P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS5N0P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS5N0P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s5.n0.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS5N0P0HoldFinished:
    """`mesh.s5.n0.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N0P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s5.n0.p0.hold`, uid 247.

    Returns one of:
      - `MeshS5N0P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N0_P0_HOLD
    PATH = "mesh.s5.n0.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N0P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS5N0P0HoldFinished

    async def __call__(self) -> MeshS5N0P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s5.n0.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS5N0P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s5.n0.p0.quench`, uid 248.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S5_N0_P0_QUENCH
    PATH = "mesh.s5.n0.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s5.n0.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS5N0P1SampleFinished:
    """`mesh.s5.n0.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N0P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s5.n0.p1.sample`, uid 253.

    Returns one of:
      - `MeshS5N0P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N0_P1_SAMPLE
    PATH = "mesh.s5.n0.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N0P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS5N0P1SampleFinished

    async def __call__(self) -> MeshS5N0P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s5.n0.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS5N0P1ArmFinished:
    """`mesh.s5.n0.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N0P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s5.n0.p1.arm`, uid 250.

    Returns one of:
      - `MeshS5N0P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N0_P1_ARM
    PATH = "mesh.s5.n0.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS5N0P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS5N0P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS5N0P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s5.n0.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS5N0P1HoldFinished:
    """`mesh.s5.n0.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N0P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s5.n0.p1.hold`, uid 251.

    Returns one of:
      - `MeshS5N0P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N0_P1_HOLD
    PATH = "mesh.s5.n0.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N0P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS5N0P1HoldFinished

    async def __call__(self) -> MeshS5N0P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s5.n0.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS5N0P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s5.n0.p1.quench`, uid 252.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S5_N0_P1_QUENCH
    PATH = "mesh.s5.n0.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s5.n0.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS5N0P2SampleFinished:
    """`mesh.s5.n0.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N0P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s5.n0.p2.sample`, uid 257.

    Returns one of:
      - `MeshS5N0P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N0_P2_SAMPLE
    PATH = "mesh.s5.n0.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N0P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS5N0P2SampleFinished

    async def __call__(self) -> MeshS5N0P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s5.n0.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS5N0P2ArmFinished:
    """`mesh.s5.n0.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N0P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s5.n0.p2.arm`, uid 254.

    Returns one of:
      - `MeshS5N0P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N0_P2_ARM
    PATH = "mesh.s5.n0.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS5N0P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS5N0P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS5N0P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s5.n0.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS5N0P2HoldFinished:
    """`mesh.s5.n0.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N0P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s5.n0.p2.hold`, uid 255.

    Returns one of:
      - `MeshS5N0P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N0_P2_HOLD
    PATH = "mesh.s5.n0.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N0P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS5N0P2HoldFinished

    async def __call__(self) -> MeshS5N0P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s5.n0.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS5N0P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s5.n0.p2.quench`, uid 256.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S5_N0_P2_QUENCH
    PATH = "mesh.s5.n0.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s5.n0.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS5N1P0SampleFinished:
    """`mesh.s5.n1.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N1P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s5.n1.p0.sample`, uid 261.

    Returns one of:
      - `MeshS5N1P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N1_P0_SAMPLE
    PATH = "mesh.s5.n1.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N1P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS5N1P0SampleFinished

    async def __call__(self) -> MeshS5N1P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s5.n1.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS5N1P0ArmFinished:
    """`mesh.s5.n1.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N1P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s5.n1.p0.arm`, uid 258.

    Returns one of:
      - `MeshS5N1P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N1_P0_ARM
    PATH = "mesh.s5.n1.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS5N1P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS5N1P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS5N1P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s5.n1.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS5N1P0HoldFinished:
    """`mesh.s5.n1.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N1P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s5.n1.p0.hold`, uid 259.

    Returns one of:
      - `MeshS5N1P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N1_P0_HOLD
    PATH = "mesh.s5.n1.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N1P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS5N1P0HoldFinished

    async def __call__(self) -> MeshS5N1P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s5.n1.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS5N1P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s5.n1.p0.quench`, uid 260.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S5_N1_P0_QUENCH
    PATH = "mesh.s5.n1.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s5.n1.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS5N1P1SampleFinished:
    """`mesh.s5.n1.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N1P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s5.n1.p1.sample`, uid 265.

    Returns one of:
      - `MeshS5N1P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N1_P1_SAMPLE
    PATH = "mesh.s5.n1.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N1P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS5N1P1SampleFinished

    async def __call__(self) -> MeshS5N1P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s5.n1.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS5N1P1ArmFinished:
    """`mesh.s5.n1.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N1P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s5.n1.p1.arm`, uid 262.

    Returns one of:
      - `MeshS5N1P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N1_P1_ARM
    PATH = "mesh.s5.n1.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS5N1P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS5N1P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS5N1P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s5.n1.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS5N1P1HoldFinished:
    """`mesh.s5.n1.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N1P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s5.n1.p1.hold`, uid 263.

    Returns one of:
      - `MeshS5N1P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N1_P1_HOLD
    PATH = "mesh.s5.n1.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N1P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS5N1P1HoldFinished

    async def __call__(self) -> MeshS5N1P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s5.n1.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS5N1P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s5.n1.p1.quench`, uid 264.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S5_N1_P1_QUENCH
    PATH = "mesh.s5.n1.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s5.n1.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS5N1P2SampleFinished:
    """`mesh.s5.n1.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N1P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s5.n1.p2.sample`, uid 269.

    Returns one of:
      - `MeshS5N1P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N1_P2_SAMPLE
    PATH = "mesh.s5.n1.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N1P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS5N1P2SampleFinished

    async def __call__(self) -> MeshS5N1P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s5.n1.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS5N1P2ArmFinished:
    """`mesh.s5.n1.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N1P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s5.n1.p2.arm`, uid 266.

    Returns one of:
      - `MeshS5N1P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N1_P2_ARM
    PATH = "mesh.s5.n1.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS5N1P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS5N1P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS5N1P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s5.n1.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS5N1P2HoldFinished:
    """`mesh.s5.n1.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N1P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s5.n1.p2.hold`, uid 267.

    Returns one of:
      - `MeshS5N1P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N1_P2_HOLD
    PATH = "mesh.s5.n1.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N1P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS5N1P2HoldFinished

    async def __call__(self) -> MeshS5N1P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s5.n1.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS5N1P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s5.n1.p2.quench`, uid 268.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S5_N1_P2_QUENCH
    PATH = "mesh.s5.n1.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s5.n1.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS5N2P0SampleFinished:
    """`mesh.s5.n2.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N2P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s5.n2.p0.sample`, uid 273.

    Returns one of:
      - `MeshS5N2P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N2_P0_SAMPLE
    PATH = "mesh.s5.n2.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N2P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS5N2P0SampleFinished

    async def __call__(self) -> MeshS5N2P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s5.n2.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS5N2P0ArmFinished:
    """`mesh.s5.n2.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N2P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s5.n2.p0.arm`, uid 270.

    Returns one of:
      - `MeshS5N2P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N2_P0_ARM
    PATH = "mesh.s5.n2.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS5N2P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS5N2P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS5N2P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s5.n2.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS5N2P0HoldFinished:
    """`mesh.s5.n2.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N2P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s5.n2.p0.hold`, uid 271.

    Returns one of:
      - `MeshS5N2P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N2_P0_HOLD
    PATH = "mesh.s5.n2.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N2P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS5N2P0HoldFinished

    async def __call__(self) -> MeshS5N2P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s5.n2.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS5N2P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s5.n2.p0.quench`, uid 272.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S5_N2_P0_QUENCH
    PATH = "mesh.s5.n2.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s5.n2.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS5N2P1SampleFinished:
    """`mesh.s5.n2.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N2P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s5.n2.p1.sample`, uid 277.

    Returns one of:
      - `MeshS5N2P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N2_P1_SAMPLE
    PATH = "mesh.s5.n2.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N2P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS5N2P1SampleFinished

    async def __call__(self) -> MeshS5N2P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s5.n2.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS5N2P1ArmFinished:
    """`mesh.s5.n2.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N2P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s5.n2.p1.arm`, uid 274.

    Returns one of:
      - `MeshS5N2P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N2_P1_ARM
    PATH = "mesh.s5.n2.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS5N2P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS5N2P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS5N2P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s5.n2.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS5N2P1HoldFinished:
    """`mesh.s5.n2.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N2P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s5.n2.p1.hold`, uid 275.

    Returns one of:
      - `MeshS5N2P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N2_P1_HOLD
    PATH = "mesh.s5.n2.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N2P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS5N2P1HoldFinished

    async def __call__(self) -> MeshS5N2P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s5.n2.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS5N2P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s5.n2.p1.quench`, uid 276.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S5_N2_P1_QUENCH
    PATH = "mesh.s5.n2.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s5.n2.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS5N2P2SampleFinished:
    """`mesh.s5.n2.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N2P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s5.n2.p2.sample`, uid 281.

    Returns one of:
      - `MeshS5N2P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N2_P2_SAMPLE
    PATH = "mesh.s5.n2.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N2P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS5N2P2SampleFinished

    async def __call__(self) -> MeshS5N2P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s5.n2.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS5N2P2ArmFinished:
    """`mesh.s5.n2.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N2P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s5.n2.p2.arm`, uid 278.

    Returns one of:
      - `MeshS5N2P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N2_P2_ARM
    PATH = "mesh.s5.n2.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS5N2P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS5N2P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS5N2P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s5.n2.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS5N2P2HoldFinished:
    """`mesh.s5.n2.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N2P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s5.n2.p2.hold`, uid 279.

    Returns one of:
      - `MeshS5N2P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N2_P2_HOLD
    PATH = "mesh.s5.n2.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N2P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS5N2P2HoldFinished

    async def __call__(self) -> MeshS5N2P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s5.n2.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS5N2P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s5.n2.p2.quench`, uid 280.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S5_N2_P2_QUENCH
    PATH = "mesh.s5.n2.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s5.n2.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS5N3P0SampleFinished:
    """`mesh.s5.n3.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N3P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s5.n3.p0.sample`, uid 285.

    Returns one of:
      - `MeshS5N3P0SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N3_P0_SAMPLE
    PATH = "mesh.s5.n3.p0.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N3P0SampleFinished, ("uint16",)),
    ])

    Finished = MeshS5N3P0SampleFinished

    async def __call__(self) -> MeshS5N3P0SampleFinished | UndeclaredResult:
        """Starts `mesh.s5.n3.p0.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS5N3P0ArmFinished:
    """`mesh.s5.n3.p0.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N3P0Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s5.n3.p0.arm`, uid 282.

    Returns one of:
      - `MeshS5N3P0ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N3_P0_ARM
    PATH = "mesh.s5.n3.p0.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS5N3P0ArmFinished, ("uint16",)),
    ])

    Finished = MeshS5N3P0ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS5N3P0ArmFinished | UndeclaredResult:
        """Starts `mesh.s5.n3.p0.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS5N3P0HoldFinished:
    """`mesh.s5.n3.p0.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N3P0Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s5.n3.p0.hold`, uid 283.

    Returns one of:
      - `MeshS5N3P0HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N3_P0_HOLD
    PATH = "mesh.s5.n3.p0.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N3P0HoldFinished, ("uint16",)),
    ])

    Finished = MeshS5N3P0HoldFinished

    async def __call__(self) -> MeshS5N3P0HoldFinished | UndeclaredResult:
        """Starts `mesh.s5.n3.p0.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS5N3P0Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s5.n3.p0.quench`, uid 284.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S5_N3_P0_QUENCH
    PATH = "mesh.s5.n3.p0.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s5.n3.p0.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS5N3P1SampleFinished:
    """`mesh.s5.n3.p1.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N3P1Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s5.n3.p1.sample`, uid 289.

    Returns one of:
      - `MeshS5N3P1SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N3_P1_SAMPLE
    PATH = "mesh.s5.n3.p1.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N3P1SampleFinished, ("uint16",)),
    ])

    Finished = MeshS5N3P1SampleFinished

    async def __call__(self) -> MeshS5N3P1SampleFinished | UndeclaredResult:
        """Starts `mesh.s5.n3.p1.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS5N3P1ArmFinished:
    """`mesh.s5.n3.p1.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N3P1Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s5.n3.p1.arm`, uid 286.

    Returns one of:
      - `MeshS5N3P1ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N3_P1_ARM
    PATH = "mesh.s5.n3.p1.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS5N3P1ArmFinished, ("uint16",)),
    ])

    Finished = MeshS5N3P1ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS5N3P1ArmFinished | UndeclaredResult:
        """Starts `mesh.s5.n3.p1.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS5N3P1HoldFinished:
    """`mesh.s5.n3.p1.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N3P1Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s5.n3.p1.hold`, uid 287.

    Returns one of:
      - `MeshS5N3P1HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N3_P1_HOLD
    PATH = "mesh.s5.n3.p1.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N3P1HoldFinished, ("uint16",)),
    ])

    Finished = MeshS5N3P1HoldFinished

    async def __call__(self) -> MeshS5N3P1HoldFinished | UndeclaredResult:
        """Starts `mesh.s5.n3.p1.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS5N3P1Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s5.n3.p1.quench`, uid 288.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S5_N3_P1_QUENCH
    PATH = "mesh.s5.n3.p1.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s5.n3.p1.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class MeshS5N3P2SampleFinished:
    """`mesh.s5.n3.p2.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N3P2Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s5.n3.p2.sample`, uid 293.

    Returns one of:
      - `MeshS5N3P2SampleFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N3_P2_SAMPLE
    PATH = "mesh.s5.n3.p2.sample"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N3P2SampleFinished, ("uint16",)),
    ])

    Finished = MeshS5N3P2SampleFinished

    async def __call__(self) -> MeshS5N3P2SampleFinished | UndeclaredResult:
        """Starts `mesh.s5.n3.p2.sample` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class MeshS5N3P2ArmFinished:
    """`mesh.s5.n3.p2.arm` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N3P2Arm(TaskBinding):
    """arm this probe across ticks

    Schema path `mesh.s5.n3.p2.arm`, uid 290.

    Returns one of:
      - `MeshS5N3P2ArmFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N3_P2_ARM
    PATH = "mesh.s5.n3.p2.arm"
    PARAMS = ("float",)
    SHAPES = build_shapes([
        (0x20, MeshS5N3P2ArmFinished, ("uint16",)),
    ])

    Finished = MeshS5N3P2ArmFinished

    async def __call__(self, *, threshold: float) -> MeshS5N3P2ArmFinished | UndeclaredResult:
        """Starts `mesh.s5.n3.p2.arm` and waits for its reply.

        Args:
            threshold: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([threshold])


@dataclass(frozen=True)
class MeshS5N3P2HoldFinished:
    """`mesh.s5.n3.p2.hold` result carried by `finished` (0x20)."""

    uid: int


class _MeshS5N3P2Hold(TaskBinding):
    """hold this probe, suspendably

    Schema path `mesh.s5.n3.p2.hold`, uid 291.

    Returns one of:
      - `MeshS5N3P2HoldFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.MESH_S5_N3_P2_HOLD
    PATH = "mesh.s5.n3.p2.hold"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, MeshS5N3P2HoldFinished, ("uint16",)),
    ])

    Finished = MeshS5N3P2HoldFinished

    async def __call__(self) -> MeshS5N3P2HoldFinished | UndeclaredResult:
        """Starts `mesh.s5.n3.p2.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _MeshS5N3P2Quench(InstantTaskBinding):
    """cut this probe now

    Schema path `mesh.s5.n3.p2.quench`, uid 292.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.MESH_S5_N3_P2_QUENCH
    PATH = "mesh.s5.n3.p2.quench"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `mesh.s5.n3.p2.quench` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class BusLinkStateProbeFinished:
    """`bus.link_state.probe` result carried by `finished` (0x20)."""

    uid: int


class _BusLinkStateProbe(TaskBinding):
    """report this task's identity

    Schema path `bus.link_state.probe`, uid 1.

    Returns one of:
      - `BusLinkStateProbeFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.BUS_LINK_STATE_PROBE
    PATH = "bus.link_state.probe"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, BusLinkStateProbeFinished, ("uint16",)),
    ])

    Finished = BusLinkStateProbeFinished

    async def __call__(self) -> BusLinkStateProbeFinished | UndeclaredResult:
        """Starts `bus.link_state.probe` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class BusLinkStateProbe2Finished:
    """`bus.link.state_probe2` result carried by `finished` (0x20)."""

    uid: int


class _BusLinkStateProbe2(TaskBinding):
    """report this task's identity

    Schema path `bus.link.state_probe2`, uid 0.

    Returns one of:
      - `BusLinkStateProbe2Finished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.BUS_LINK_STATE_PROBE2
    PATH = "bus.link.state_probe2"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, BusLinkStateProbe2Finished, ("uint16",)),
    ])

    Finished = BusLinkStateProbe2Finished

    async def __call__(self) -> BusLinkStateProbe2Finished | UndeclaredResult:
        """Starts `bus.link.state_probe2` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _BusReserveEmergencyHalt(InstantTaskBinding):
    """halt everything

    Schema path `bus.reserve.emergency_halt`, uid 4.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.BUS_RESERVE_EMERGENCY_HALT
    PATH = "bus.reserve.emergency_halt"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `bus.reserve.emergency_halt` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class BusReserveDiagnosticFinished:
    """`bus.reserve.diagnostic` result carried by `finished` (0x20)."""

    uid: int


class _BusReserveDiagnostic(TaskBinding):
    """report this task's identity

    Schema path `bus.reserve.diagnostic`, uid 3.

    Returns one of:
      - `BusReserveDiagnosticFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.BUS_RESERVE_DIAGNOSTIC
    PATH = "bus.reserve.diagnostic"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, BusReserveDiagnosticFinished, ("uint16",)),
    ])

    Finished = BusReserveDiagnosticFinished

    async def __call__(self) -> BusReserveDiagnosticFinished | UndeclaredResult:
        """Starts `bus.reserve.diagnostic` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class BusReserveAuditFinished:
    """`bus.reserve.audit` result carried by `finished` (0x20)."""

    uid: int


class _BusReserveAudit(TaskBinding):
    """report this task's identity

    Schema path `bus.reserve.audit`, uid 2.

    Returns one of:
      - `BusReserveAuditFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.BUS_RESERVE_AUDIT
    PATH = "bus.reserve.audit"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, BusReserveAuditFinished, ("uint16",)),
    ])

    Finished = BusReserveAuditFinished

    async def __call__(self) -> BusReserveAuditFinished | UndeclaredResult:
        """Starts `bus.reserve.audit` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class CensusFinished:
    """`census` result carried by `finished` (0x20)."""

    uid: int


class _Census(TaskBinding):
    """report the root task's identity

    Schema path `census`, uid 5.

    Returns one of:
      - `CensusFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.CENSUS
    PATH = "census"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, CensusFinished, ("uint16",)),
    ])

    Finished = CensusFinished

    async def __call__(self) -> CensusFinished | UndeclaredResult:
        """Starts `census` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _BusReserveScope(Scope):
    """three ordinary siblings, low in the uid space

    Schema scope `bus.reserve`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.emergency_halt = _BusReserveEmergencyHalt(client)
        self.diagnostic = _BusReserveDiagnostic(client)
        self.audit = _BusReserveAudit(client)


class _BusLinkScope(Scope):
    """link, as a scope whose child carries the underscore instead

    Schema scope `bus.link`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.state_probe2 = _BusLinkStateProbe2(client)


class _BusLinkStateScope(Scope):
    """link state, as one scope named with an underscore

    Schema scope `bus.link_state`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.probe = _BusLinkStateProbe(client)


class _BusScope(Scope):
    """the concrete side of the tree

    Schema scope `bus`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.link_state = _BusLinkStateScope(client)
        self.link = _BusLinkScope(client)
        self.reserve = _BusReserveScope(client)


class _MeshS5N3P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s5.n3.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS5N3P2Sample(client)
        self.arm = _MeshS5N3P2Arm(client)
        self.hold = _MeshS5N3P2Hold(client)
        self.quench = _MeshS5N3P2Quench(client)


class _MeshS5N3P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s5.n3.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS5N3P1Sample(client)
        self.arm = _MeshS5N3P1Arm(client)
        self.hold = _MeshS5N3P1Hold(client)
        self.quench = _MeshS5N3P1Quench(client)


class _MeshS5N3P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s5.n3.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS5N3P0Sample(client)
        self.arm = _MeshS5N3P0Arm(client)
        self.hold = _MeshS5N3P0Hold(client)
        self.quench = _MeshS5N3P0Quench(client)


class _MeshS5N3Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s5.n3`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS5N3P0Scope(client)
        self.p1 = _MeshS5N3P1Scope(client)
        self.p2 = _MeshS5N3P2Scope(client)


class _MeshS5N2P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s5.n2.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS5N2P2Sample(client)
        self.arm = _MeshS5N2P2Arm(client)
        self.hold = _MeshS5N2P2Hold(client)
        self.quench = _MeshS5N2P2Quench(client)


class _MeshS5N2P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s5.n2.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS5N2P1Sample(client)
        self.arm = _MeshS5N2P1Arm(client)
        self.hold = _MeshS5N2P1Hold(client)
        self.quench = _MeshS5N2P1Quench(client)


class _MeshS5N2P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s5.n2.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS5N2P0Sample(client)
        self.arm = _MeshS5N2P0Arm(client)
        self.hold = _MeshS5N2P0Hold(client)
        self.quench = _MeshS5N2P0Quench(client)


class _MeshS5N2Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s5.n2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS5N2P0Scope(client)
        self.p1 = _MeshS5N2P1Scope(client)
        self.p2 = _MeshS5N2P2Scope(client)


class _MeshS5N1P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s5.n1.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS5N1P2Sample(client)
        self.arm = _MeshS5N1P2Arm(client)
        self.hold = _MeshS5N1P2Hold(client)
        self.quench = _MeshS5N1P2Quench(client)


class _MeshS5N1P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s5.n1.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS5N1P1Sample(client)
        self.arm = _MeshS5N1P1Arm(client)
        self.hold = _MeshS5N1P1Hold(client)
        self.quench = _MeshS5N1P1Quench(client)


class _MeshS5N1P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s5.n1.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS5N1P0Sample(client)
        self.arm = _MeshS5N1P0Arm(client)
        self.hold = _MeshS5N1P0Hold(client)
        self.quench = _MeshS5N1P0Quench(client)


class _MeshS5N1Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s5.n1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS5N1P0Scope(client)
        self.p1 = _MeshS5N1P1Scope(client)
        self.p2 = _MeshS5N1P2Scope(client)


class _MeshS5N0P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s5.n0.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS5N0P2Sample(client)
        self.arm = _MeshS5N0P2Arm(client)
        self.hold = _MeshS5N0P2Hold(client)
        self.quench = _MeshS5N0P2Quench(client)


class _MeshS5N0P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s5.n0.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS5N0P1Sample(client)
        self.arm = _MeshS5N0P1Arm(client)
        self.hold = _MeshS5N0P1Hold(client)
        self.quench = _MeshS5N0P1Quench(client)


class _MeshS5N0P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s5.n0.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS5N0P0Sample(client)
        self.arm = _MeshS5N0P0Arm(client)
        self.hold = _MeshS5N0P0Hold(client)
        self.quench = _MeshS5N0P0Quench(client)


class _MeshS5N0Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s5.n0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS5N0P0Scope(client)
        self.p1 = _MeshS5N0P1Scope(client)
        self.p2 = _MeshS5N0P2Scope(client)


class _MeshS5Scope(Scope):
    """one mesh segment

    Schema scope `mesh.s5`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.n0 = _MeshS5N0Scope(client)
        self.n1 = _MeshS5N1Scope(client)
        self.n2 = _MeshS5N2Scope(client)
        self.n3 = _MeshS5N3Scope(client)


class _MeshS4N3P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s4.n3.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS4N3P2Sample(client)
        self.arm = _MeshS4N3P2Arm(client)
        self.hold = _MeshS4N3P2Hold(client)
        self.quench = _MeshS4N3P2Quench(client)


class _MeshS4N3P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s4.n3.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS4N3P1Sample(client)
        self.arm = _MeshS4N3P1Arm(client)
        self.hold = _MeshS4N3P1Hold(client)
        self.quench = _MeshS4N3P1Quench(client)


class _MeshS4N3P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s4.n3.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS4N3P0Sample(client)
        self.arm = _MeshS4N3P0Arm(client)
        self.hold = _MeshS4N3P0Hold(client)
        self.quench = _MeshS4N3P0Quench(client)


class _MeshS4N3Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s4.n3`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS4N3P0Scope(client)
        self.p1 = _MeshS4N3P1Scope(client)
        self.p2 = _MeshS4N3P2Scope(client)


class _MeshS4N2P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s4.n2.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS4N2P2Sample(client)
        self.arm = _MeshS4N2P2Arm(client)
        self.hold = _MeshS4N2P2Hold(client)
        self.quench = _MeshS4N2P2Quench(client)


class _MeshS4N2P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s4.n2.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS4N2P1Sample(client)
        self.arm = _MeshS4N2P1Arm(client)
        self.hold = _MeshS4N2P1Hold(client)
        self.quench = _MeshS4N2P1Quench(client)


class _MeshS4N2P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s4.n2.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS4N2P0Sample(client)
        self.arm = _MeshS4N2P0Arm(client)
        self.hold = _MeshS4N2P0Hold(client)
        self.quench = _MeshS4N2P0Quench(client)


class _MeshS4N2Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s4.n2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS4N2P0Scope(client)
        self.p1 = _MeshS4N2P1Scope(client)
        self.p2 = _MeshS4N2P2Scope(client)


class _MeshS4N1P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s4.n1.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS4N1P2Sample(client)
        self.arm = _MeshS4N1P2Arm(client)
        self.hold = _MeshS4N1P2Hold(client)
        self.quench = _MeshS4N1P2Quench(client)


class _MeshS4N1P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s4.n1.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS4N1P1Sample(client)
        self.arm = _MeshS4N1P1Arm(client)
        self.hold = _MeshS4N1P1Hold(client)
        self.quench = _MeshS4N1P1Quench(client)


class _MeshS4N1P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s4.n1.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS4N1P0Sample(client)
        self.arm = _MeshS4N1P0Arm(client)
        self.hold = _MeshS4N1P0Hold(client)
        self.quench = _MeshS4N1P0Quench(client)


class _MeshS4N1Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s4.n1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS4N1P0Scope(client)
        self.p1 = _MeshS4N1P1Scope(client)
        self.p2 = _MeshS4N1P2Scope(client)


class _MeshS4N0P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s4.n0.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS4N0P2Sample(client)
        self.arm = _MeshS4N0P2Arm(client)
        self.hold = _MeshS4N0P2Hold(client)
        self.quench = _MeshS4N0P2Quench(client)


class _MeshS4N0P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s4.n0.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS4N0P1Sample(client)
        self.arm = _MeshS4N0P1Arm(client)
        self.hold = _MeshS4N0P1Hold(client)
        self.quench = _MeshS4N0P1Quench(client)


class _MeshS4N0P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s4.n0.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS4N0P0Sample(client)
        self.arm = _MeshS4N0P0Arm(client)
        self.hold = _MeshS4N0P0Hold(client)
        self.quench = _MeshS4N0P0Quench(client)


class _MeshS4N0Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s4.n0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS4N0P0Scope(client)
        self.p1 = _MeshS4N0P1Scope(client)
        self.p2 = _MeshS4N0P2Scope(client)


class _MeshS4Scope(Scope):
    """one mesh segment

    Schema scope `mesh.s4`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.n0 = _MeshS4N0Scope(client)
        self.n1 = _MeshS4N1Scope(client)
        self.n2 = _MeshS4N2Scope(client)
        self.n3 = _MeshS4N3Scope(client)


class _MeshS3N3P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s3.n3.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS3N3P2Sample(client)
        self.arm = _MeshS3N3P2Arm(client)
        self.hold = _MeshS3N3P2Hold(client)
        self.quench = _MeshS3N3P2Quench(client)


class _MeshS3N3P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s3.n3.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS3N3P1Sample(client)
        self.arm = _MeshS3N3P1Arm(client)
        self.hold = _MeshS3N3P1Hold(client)
        self.quench = _MeshS3N3P1Quench(client)


class _MeshS3N3P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s3.n3.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS3N3P0Sample(client)
        self.arm = _MeshS3N3P0Arm(client)
        self.hold = _MeshS3N3P0Hold(client)
        self.quench = _MeshS3N3P0Quench(client)


class _MeshS3N3Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s3.n3`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS3N3P0Scope(client)
        self.p1 = _MeshS3N3P1Scope(client)
        self.p2 = _MeshS3N3P2Scope(client)


class _MeshS3N2P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s3.n2.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS3N2P2Sample(client)
        self.arm = _MeshS3N2P2Arm(client)
        self.hold = _MeshS3N2P2Hold(client)
        self.quench = _MeshS3N2P2Quench(client)


class _MeshS3N2P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s3.n2.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS3N2P1Sample(client)
        self.arm = _MeshS3N2P1Arm(client)
        self.hold = _MeshS3N2P1Hold(client)
        self.quench = _MeshS3N2P1Quench(client)


class _MeshS3N2P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s3.n2.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS3N2P0Sample(client)
        self.arm = _MeshS3N2P0Arm(client)
        self.hold = _MeshS3N2P0Hold(client)
        self.quench = _MeshS3N2P0Quench(client)


class _MeshS3N2Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s3.n2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS3N2P0Scope(client)
        self.p1 = _MeshS3N2P1Scope(client)
        self.p2 = _MeshS3N2P2Scope(client)


class _MeshS3N1P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s3.n1.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS3N1P2Sample(client)
        self.arm = _MeshS3N1P2Arm(client)
        self.hold = _MeshS3N1P2Hold(client)
        self.quench = _MeshS3N1P2Quench(client)


class _MeshS3N1P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s3.n1.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS3N1P1Sample(client)
        self.arm = _MeshS3N1P1Arm(client)
        self.hold = _MeshS3N1P1Hold(client)
        self.quench = _MeshS3N1P1Quench(client)


class _MeshS3N1P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s3.n1.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS3N1P0Sample(client)
        self.arm = _MeshS3N1P0Arm(client)
        self.hold = _MeshS3N1P0Hold(client)
        self.quench = _MeshS3N1P0Quench(client)


class _MeshS3N1Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s3.n1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS3N1P0Scope(client)
        self.p1 = _MeshS3N1P1Scope(client)
        self.p2 = _MeshS3N1P2Scope(client)


class _MeshS3N0P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s3.n0.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS3N0P2Sample(client)
        self.arm = _MeshS3N0P2Arm(client)
        self.hold = _MeshS3N0P2Hold(client)
        self.quench = _MeshS3N0P2Quench(client)


class _MeshS3N0P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s3.n0.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS3N0P1Sample(client)
        self.arm = _MeshS3N0P1Arm(client)
        self.hold = _MeshS3N0P1Hold(client)
        self.quench = _MeshS3N0P1Quench(client)


class _MeshS3N0P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s3.n0.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS3N0P0Sample(client)
        self.arm = _MeshS3N0P0Arm(client)
        self.hold = _MeshS3N0P0Hold(client)
        self.quench = _MeshS3N0P0Quench(client)


class _MeshS3N0Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s3.n0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS3N0P0Scope(client)
        self.p1 = _MeshS3N0P1Scope(client)
        self.p2 = _MeshS3N0P2Scope(client)


class _MeshS3Scope(Scope):
    """one mesh segment

    Schema scope `mesh.s3`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.n0 = _MeshS3N0Scope(client)
        self.n1 = _MeshS3N1Scope(client)
        self.n2 = _MeshS3N2Scope(client)
        self.n3 = _MeshS3N3Scope(client)


class _MeshS2N3P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s2.n3.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS2N3P2Sample(client)
        self.arm = _MeshS2N3P2Arm(client)
        self.hold = _MeshS2N3P2Hold(client)
        self.quench = _MeshS2N3P2Quench(client)


class _MeshS2N3P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s2.n3.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS2N3P1Sample(client)
        self.arm = _MeshS2N3P1Arm(client)
        self.hold = _MeshS2N3P1Hold(client)
        self.quench = _MeshS2N3P1Quench(client)


class _MeshS2N3P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s2.n3.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS2N3P0Sample(client)
        self.arm = _MeshS2N3P0Arm(client)
        self.hold = _MeshS2N3P0Hold(client)
        self.quench = _MeshS2N3P0Quench(client)


class _MeshS2N3Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s2.n3`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS2N3P0Scope(client)
        self.p1 = _MeshS2N3P1Scope(client)
        self.p2 = _MeshS2N3P2Scope(client)


class _MeshS2N2P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s2.n2.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS2N2P2Sample(client)
        self.arm = _MeshS2N2P2Arm(client)
        self.hold = _MeshS2N2P2Hold(client)
        self.quench = _MeshS2N2P2Quench(client)


class _MeshS2N2P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s2.n2.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS2N2P1Sample(client)
        self.arm = _MeshS2N2P1Arm(client)
        self.hold = _MeshS2N2P1Hold(client)
        self.quench = _MeshS2N2P1Quench(client)


class _MeshS2N2P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s2.n2.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS2N2P0Sample(client)
        self.arm = _MeshS2N2P0Arm(client)
        self.hold = _MeshS2N2P0Hold(client)
        self.quench = _MeshS2N2P0Quench(client)


class _MeshS2N2Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s2.n2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS2N2P0Scope(client)
        self.p1 = _MeshS2N2P1Scope(client)
        self.p2 = _MeshS2N2P2Scope(client)


class _MeshS2N1P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s2.n1.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS2N1P2Sample(client)
        self.arm = _MeshS2N1P2Arm(client)
        self.hold = _MeshS2N1P2Hold(client)
        self.quench = _MeshS2N1P2Quench(client)


class _MeshS2N1P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s2.n1.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS2N1P1Sample(client)
        self.arm = _MeshS2N1P1Arm(client)
        self.hold = _MeshS2N1P1Hold(client)
        self.quench = _MeshS2N1P1Quench(client)


class _MeshS2N1P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s2.n1.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS2N1P0Sample(client)
        self.arm = _MeshS2N1P0Arm(client)
        self.hold = _MeshS2N1P0Hold(client)
        self.quench = _MeshS2N1P0Quench(client)


class _MeshS2N1Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s2.n1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS2N1P0Scope(client)
        self.p1 = _MeshS2N1P1Scope(client)
        self.p2 = _MeshS2N1P2Scope(client)


class _MeshS2N0P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s2.n0.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS2N0P2Sample(client)
        self.arm = _MeshS2N0P2Arm(client)
        self.hold = _MeshS2N0P2Hold(client)
        self.quench = _MeshS2N0P2Quench(client)


class _MeshS2N0P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s2.n0.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS2N0P1Sample(client)
        self.arm = _MeshS2N0P1Arm(client)
        self.hold = _MeshS2N0P1Hold(client)
        self.quench = _MeshS2N0P1Quench(client)


class _MeshS2N0P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s2.n0.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS2N0P0Sample(client)
        self.arm = _MeshS2N0P0Arm(client)
        self.hold = _MeshS2N0P0Hold(client)
        self.quench = _MeshS2N0P0Quench(client)


class _MeshS2N0Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s2.n0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS2N0P0Scope(client)
        self.p1 = _MeshS2N0P1Scope(client)
        self.p2 = _MeshS2N0P2Scope(client)


class _MeshS2Scope(Scope):
    """one mesh segment

    Schema scope `mesh.s2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.n0 = _MeshS2N0Scope(client)
        self.n1 = _MeshS2N1Scope(client)
        self.n2 = _MeshS2N2Scope(client)
        self.n3 = _MeshS2N3Scope(client)


class _MeshS1N3P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s1.n3.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS1N3P2Sample(client)
        self.arm = _MeshS1N3P2Arm(client)
        self.hold = _MeshS1N3P2Hold(client)
        self.quench = _MeshS1N3P2Quench(client)


class _MeshS1N3P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s1.n3.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS1N3P1Sample(client)
        self.arm = _MeshS1N3P1Arm(client)
        self.hold = _MeshS1N3P1Hold(client)
        self.quench = _MeshS1N3P1Quench(client)


class _MeshS1N3P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s1.n3.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS1N3P0Sample(client)
        self.arm = _MeshS1N3P0Arm(client)
        self.hold = _MeshS1N3P0Hold(client)
        self.quench = _MeshS1N3P0Quench(client)


class _MeshS1N3Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s1.n3`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS1N3P0Scope(client)
        self.p1 = _MeshS1N3P1Scope(client)
        self.p2 = _MeshS1N3P2Scope(client)


class _MeshS1N2P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s1.n2.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS1N2P2Sample(client)
        self.arm = _MeshS1N2P2Arm(client)
        self.hold = _MeshS1N2P2Hold(client)
        self.quench = _MeshS1N2P2Quench(client)


class _MeshS1N2P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s1.n2.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS1N2P1Sample(client)
        self.arm = _MeshS1N2P1Arm(client)
        self.hold = _MeshS1N2P1Hold(client)
        self.quench = _MeshS1N2P1Quench(client)


class _MeshS1N2P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s1.n2.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS1N2P0Sample(client)
        self.arm = _MeshS1N2P0Arm(client)
        self.hold = _MeshS1N2P0Hold(client)
        self.quench = _MeshS1N2P0Quench(client)


class _MeshS1N2Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s1.n2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS1N2P0Scope(client)
        self.p1 = _MeshS1N2P1Scope(client)
        self.p2 = _MeshS1N2P2Scope(client)


class _MeshS1N1P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s1.n1.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS1N1P2Sample(client)
        self.arm = _MeshS1N1P2Arm(client)
        self.hold = _MeshS1N1P2Hold(client)
        self.quench = _MeshS1N1P2Quench(client)


class _MeshS1N1P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s1.n1.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS1N1P1Sample(client)
        self.arm = _MeshS1N1P1Arm(client)
        self.hold = _MeshS1N1P1Hold(client)
        self.quench = _MeshS1N1P1Quench(client)


class _MeshS1N1P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s1.n1.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS1N1P0Sample(client)
        self.arm = _MeshS1N1P0Arm(client)
        self.hold = _MeshS1N1P0Hold(client)
        self.quench = _MeshS1N1P0Quench(client)


class _MeshS1N1Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s1.n1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS1N1P0Scope(client)
        self.p1 = _MeshS1N1P1Scope(client)
        self.p2 = _MeshS1N1P2Scope(client)


class _MeshS1N0P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s1.n0.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS1N0P2Sample(client)
        self.arm = _MeshS1N0P2Arm(client)
        self.hold = _MeshS1N0P2Hold(client)
        self.quench = _MeshS1N0P2Quench(client)


class _MeshS1N0P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s1.n0.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS1N0P1Sample(client)
        self.arm = _MeshS1N0P1Arm(client)
        self.hold = _MeshS1N0P1Hold(client)
        self.quench = _MeshS1N0P1Quench(client)


class _MeshS1N0P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s1.n0.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS1N0P0Sample(client)
        self.arm = _MeshS1N0P0Arm(client)
        self.hold = _MeshS1N0P0Hold(client)
        self.quench = _MeshS1N0P0Quench(client)


class _MeshS1N0Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s1.n0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS1N0P0Scope(client)
        self.p1 = _MeshS1N0P1Scope(client)
        self.p2 = _MeshS1N0P2Scope(client)


class _MeshS1Scope(Scope):
    """one mesh segment

    Schema scope `mesh.s1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.n0 = _MeshS1N0Scope(client)
        self.n1 = _MeshS1N1Scope(client)
        self.n2 = _MeshS1N2Scope(client)
        self.n3 = _MeshS1N3Scope(client)


class _MeshS0N3P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s0.n3.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS0N3P2Sample(client)
        self.arm = _MeshS0N3P2Arm(client)
        self.hold = _MeshS0N3P2Hold(client)
        self.quench = _MeshS0N3P2Quench(client)


class _MeshS0N3P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s0.n3.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS0N3P1Sample(client)
        self.arm = _MeshS0N3P1Arm(client)
        self.hold = _MeshS0N3P1Hold(client)
        self.quench = _MeshS0N3P1Quench(client)


class _MeshS0N3P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s0.n3.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS0N3P0Sample(client)
        self.arm = _MeshS0N3P0Arm(client)
        self.hold = _MeshS0N3P0Hold(client)
        self.quench = _MeshS0N3P0Quench(client)


class _MeshS0N3Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s0.n3`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS0N3P0Scope(client)
        self.p1 = _MeshS0N3P1Scope(client)
        self.p2 = _MeshS0N3P2Scope(client)


class _MeshS0N2P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s0.n2.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS0N2P2Sample(client)
        self.arm = _MeshS0N2P2Arm(client)
        self.hold = _MeshS0N2P2Hold(client)
        self.quench = _MeshS0N2P2Quench(client)


class _MeshS0N2P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s0.n2.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS0N2P1Sample(client)
        self.arm = _MeshS0N2P1Arm(client)
        self.hold = _MeshS0N2P1Hold(client)
        self.quench = _MeshS0N2P1Quench(client)


class _MeshS0N2P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s0.n2.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS0N2P0Sample(client)
        self.arm = _MeshS0N2P0Arm(client)
        self.hold = _MeshS0N2P0Hold(client)
        self.quench = _MeshS0N2P0Quench(client)


class _MeshS0N2Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s0.n2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS0N2P0Scope(client)
        self.p1 = _MeshS0N2P1Scope(client)
        self.p2 = _MeshS0N2P2Scope(client)


class _MeshS0N1P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s0.n1.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS0N1P2Sample(client)
        self.arm = _MeshS0N1P2Arm(client)
        self.hold = _MeshS0N1P2Hold(client)
        self.quench = _MeshS0N1P2Quench(client)


class _MeshS0N1P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s0.n1.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS0N1P1Sample(client)
        self.arm = _MeshS0N1P1Arm(client)
        self.hold = _MeshS0N1P1Hold(client)
        self.quench = _MeshS0N1P1Quench(client)


class _MeshS0N1P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s0.n1.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS0N1P0Sample(client)
        self.arm = _MeshS0N1P0Arm(client)
        self.hold = _MeshS0N1P0Hold(client)
        self.quench = _MeshS0N1P0Quench(client)


class _MeshS0N1Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s0.n1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS0N1P0Scope(client)
        self.p1 = _MeshS0N1P1Scope(client)
        self.p2 = _MeshS0N1P2Scope(client)


class _MeshS0N0P2Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s0.n0.p2`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS0N0P2Sample(client)
        self.arm = _MeshS0N0P2Arm(client)
        self.hold = _MeshS0N0P2Hold(client)
        self.quench = _MeshS0N0P2Quench(client)


class _MeshS0N0P1Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s0.n0.p1`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS0N0P1Sample(client)
        self.arm = _MeshS0N0P1Arm(client)
        self.hold = _MeshS0N0P1Hold(client)
        self.quench = _MeshS0N0P1Quench(client)


class _MeshS0N0P0Scope(Scope):
    """one probe on a node

    Schema scope `mesh.s0.n0.p0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.sample = _MeshS0N0P0Sample(client)
        self.arm = _MeshS0N0P0Arm(client)
        self.hold = _MeshS0N0P0Hold(client)
        self.quench = _MeshS0N0P0Quench(client)


class _MeshS0N0Scope(Scope):
    """one node within a segment

    Schema scope `mesh.s0.n0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.p0 = _MeshS0N0P0Scope(client)
        self.p1 = _MeshS0N0P1Scope(client)
        self.p2 = _MeshS0N0P2Scope(client)


class _MeshS0Scope(Scope):
    """one mesh segment

    Schema scope `mesh.s0`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.n0 = _MeshS0N0Scope(client)
        self.n1 = _MeshS0N1Scope(client)
        self.n2 = _MeshS0N2Scope(client)
        self.n3 = _MeshS0N3Scope(client)


class _MeshScope(Scope):
    """the segmented probe mesh

    Schema scope `mesh`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.s0 = _MeshS0Scope(client)
        self.s1 = _MeshS1Scope(client)
        self.s2 = _MeshS2Scope(client)
        self.s3 = _MeshS3Scope(client)
        self.s4 = _MeshS4Scope(client)
        self.s5 = _MeshS5Scope(client)


class Tasks(Scope):
    """The project's task tree, mirroring the schema's scopes.

    Construct it with a live `Client`; every task below is an
    awaitable call at the same path the schema declares.
    """

    UID_BYTES = UID_BYTES

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.mesh = _MeshScope(client)
        self.bus = _BusScope(client)
        self.census = _Census(client)
