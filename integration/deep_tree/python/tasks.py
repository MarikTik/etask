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

SCHEMA_FINGERPRINT = 0x1AED434F487801AA
"""The wire contract this client speaks, as eight bytes.

Covers every uid, argument list, result shape and link policy in the
schema this was generated from. The device sends its own at connect; if
the two differ, the peers were built from different schemas and the
client refuses the link rather than trading frames whose uids it would
misread.
"""


class TaskId(IntEnum):
    """Every task's wire uid - the same values as `global::task_id` in C++."""

    MESH_S0_N0_P0_SAMPLE = 37421
    MESH_S0_N0_P0_ARM = 45109
    MESH_S0_N0_P0_HOLD = 44658
    MESH_S0_N0_P0_QUENCH = 8431
    MESH_S0_N0_P1_SAMPLE = 23732
    MESH_S0_N0_P1_ARM = 17224
    MESH_S0_N0_P1_HOLD = 20931
    MESH_S0_N0_P1_QUENCH = 10542
    MESH_S0_N0_P2_SAMPLE = 41553
    MESH_S0_N0_P2_ARM = 51892
    MESH_S0_N0_P2_HOLD = 46135
    MESH_S0_N0_P2_QUENCH = 15195
    MESH_S0_N1_P0_SAMPLE = 36345
    MESH_S0_N1_P0_ARM = 28042
    MESH_S0_N1_P0_HOLD = 12627
    MESH_S0_N1_P0_QUENCH = 35228
    MESH_S0_N1_P1_SAMPLE = 54212
    MESH_S0_N1_P1_ARM = 13780
    MESH_S0_N1_P1_HOLD = 53037
    MESH_S0_N1_P1_QUENCH = 56462
    MESH_S0_N1_P2_SAMPLE = 3537
    MESH_S0_N1_P2_ARM = 37151
    MESH_S0_N1_P2_HOLD = 38689
    MESH_S0_N1_P2_QUENCH = 59117
    MESH_S0_N2_P0_SAMPLE = 44976
    MESH_S0_N2_P0_ARM = 55822
    MESH_S0_N2_P0_HOLD = 47677
    MESH_S0_N2_P0_QUENCH = 11124
    MESH_S0_N2_P1_SAMPLE = 19818
    MESH_S0_N2_P1_ARM = 63540
    MESH_S0_N2_P1_HOLD = 10366
    MESH_S0_N2_P1_QUENCH = 18636
    MESH_S0_N2_P2_SAMPLE = 11520
    MESH_S0_N2_P2_ARM = 46651
    MESH_S0_N2_P2_HOLD = 12792
    MESH_S0_N2_P2_QUENCH = 22530
    MESH_S0_N3_P0_SAMPLE = 11539
    MESH_S0_N3_P0_ARM = 47555
    MESH_S0_N3_P0_HOLD = 12158
    MESH_S0_N3_P0_QUENCH = 486
    MESH_S0_N3_P1_SAMPLE = 37186
    MESH_S0_N3_P1_ARM = 25458
    MESH_S0_N3_P1_HOLD = 64765
    MESH_S0_N3_P1_QUENCH = 21537
    MESH_S0_N3_P2_SAMPLE = 19705
    MESH_S0_N3_P2_ARM = 21311
    MESH_S0_N3_P2_HOLD = 17048
    MESH_S0_N3_P2_QUENCH = 18608
    MESH_S1_N0_P0_SAMPLE = 39285
    MESH_S1_N0_P0_ARM = 36249
    MESH_S1_N0_P0_HOLD = 33267
    MESH_S1_N0_P0_QUENCH = 11006
    MESH_S1_N0_P1_SAMPLE = 13509
    MESH_S1_N0_P1_ARM = 29029
    MESH_S1_N0_P1_HOLD = 61501
    MESH_S1_N0_P1_QUENCH = 28716
    MESH_S1_N0_P2_SAMPLE = 14900
    MESH_S1_N0_P2_ARM = 3269
    MESH_S1_N0_P2_HOLD = 41765
    MESH_S1_N0_P2_QUENCH = 41938
    MESH_S1_N1_P0_SAMPLE = 14964
    MESH_S1_N1_P0_ARM = 28124
    MESH_S1_N1_P0_HOLD = 53812
    MESH_S1_N1_P0_QUENCH = 15193
    MESH_S1_N1_P1_SAMPLE = 18632
    MESH_S1_N1_P1_ARM = 55432
    MESH_S1_N1_P1_HOLD = 64454
    MESH_S1_N1_P1_QUENCH = 53130
    MESH_S1_N1_P2_SAMPLE = 34045
    MESH_S1_N1_P2_ARM = 60443
    MESH_S1_N1_P2_HOLD = 24811
    MESH_S1_N1_P2_QUENCH = 17486
    MESH_S1_N2_P0_SAMPLE = 59804
    MESH_S1_N2_P0_ARM = 60970
    MESH_S1_N2_P0_HOLD = 38423
    MESH_S1_N2_P0_QUENCH = 46512
    MESH_S1_N2_P1_SAMPLE = 60332
    MESH_S1_N2_P1_ARM = 40602
    MESH_S1_N2_P1_HOLD = 50904
    MESH_S1_N2_P1_QUENCH = 27821
    MESH_S1_N2_P2_SAMPLE = 4308
    MESH_S1_N2_P2_ARM = 27846
    MESH_S1_N2_P2_HOLD = 64056
    MESH_S1_N2_P2_QUENCH = 43450
    MESH_S1_N3_P0_SAMPLE = 59666
    MESH_S1_N3_P0_ARM = 48490
    MESH_S1_N3_P0_HOLD = 61198
    MESH_S1_N3_P0_QUENCH = 37161
    MESH_S1_N3_P1_SAMPLE = 29865
    MESH_S1_N3_P1_ARM = 18401
    MESH_S1_N3_P1_HOLD = 48947
    MESH_S1_N3_P1_QUENCH = 697
    MESH_S1_N3_P2_SAMPLE = 40532
    MESH_S1_N3_P2_ARM = 3887
    MESH_S1_N3_P2_HOLD = 1920
    MESH_S1_N3_P2_QUENCH = 28640
    MESH_S2_N0_P0_SAMPLE = 30090
    MESH_S2_N0_P0_ARM = 34650
    MESH_S2_N0_P0_HOLD = 39322
    MESH_S2_N0_P0_QUENCH = 9783
    MESH_S2_N0_P1_SAMPLE = 32908
    MESH_S2_N0_P1_ARM = 2107
    MESH_S2_N0_P1_HOLD = 49512
    MESH_S2_N0_P1_QUENCH = 16300
    MESH_S2_N0_P2_SAMPLE = 35088
    MESH_S2_N0_P2_ARM = 44755
    MESH_S2_N0_P2_HOLD = 7183
    MESH_S2_N0_P2_QUENCH = 7056
    MESH_S2_N1_P0_SAMPLE = 43294
    MESH_S2_N1_P0_ARM = 22674
    MESH_S2_N1_P0_HOLD = 55171
    MESH_S2_N1_P0_QUENCH = 17050
    MESH_S2_N1_P1_SAMPLE = 42707
    MESH_S2_N1_P1_ARM = 53214
    MESH_S2_N1_P1_HOLD = 28474
    MESH_S2_N1_P1_QUENCH = 23054
    MESH_S2_N1_P2_SAMPLE = 38556
    MESH_S2_N1_P2_ARM = 38282
    MESH_S2_N1_P2_HOLD = 9839
    MESH_S2_N1_P2_QUENCH = 21148
    MESH_S2_N2_P0_SAMPLE = 9603
    MESH_S2_N2_P0_ARM = 30738
    MESH_S2_N2_P0_HOLD = 44390
    MESH_S2_N2_P0_QUENCH = 24899
    MESH_S2_N2_P1_SAMPLE = 21164
    MESH_S2_N2_P1_ARM = 22989
    MESH_S2_N2_P1_HOLD = 39829
    MESH_S2_N2_P1_QUENCH = 30781
    MESH_S2_N2_P2_SAMPLE = 40098
    MESH_S2_N2_P2_ARM = 35484
    MESH_S2_N2_P2_HOLD = 6195
    MESH_S2_N2_P2_QUENCH = 4742
    MESH_S2_N3_P0_SAMPLE = 21361
    MESH_S2_N3_P0_ARM = 31697
    MESH_S2_N3_P0_HOLD = 14457
    MESH_S2_N3_P0_QUENCH = 16594
    MESH_S2_N3_P1_SAMPLE = 35769
    MESH_S2_N3_P1_ARM = 5767
    MESH_S2_N3_P1_HOLD = 7506
    MESH_S2_N3_P1_QUENCH = 21867
    MESH_S2_N3_P2_SAMPLE = 9159
    MESH_S2_N3_P2_ARM = 12356
    MESH_S2_N3_P2_HOLD = 42930
    MESH_S2_N3_P2_QUENCH = 33575
    MESH_S3_N0_P0_SAMPLE = 28690
    MESH_S3_N0_P0_ARM = 57576
    MESH_S3_N0_P0_HOLD = 28066
    MESH_S3_N0_P0_QUENCH = 6511
    MESH_S3_N0_P1_SAMPLE = 55179
    MESH_S3_N0_P1_ARM = 56848
    MESH_S3_N0_P1_HOLD = 1600
    MESH_S3_N0_P1_QUENCH = 19856
    MESH_S3_N0_P2_SAMPLE = 33782
    MESH_S3_N0_P2_ARM = 36305
    MESH_S3_N0_P2_HOLD = 21338
    MESH_S3_N0_P2_QUENCH = 20582
    MESH_S3_N1_P0_SAMPLE = 44344
    MESH_S3_N1_P0_ARM = 39787
    MESH_S3_N1_P0_HOLD = 44506
    MESH_S3_N1_P0_QUENCH = 51792
    MESH_S3_N1_P1_SAMPLE = 59806
    MESH_S3_N1_P1_ARM = 48391
    MESH_S3_N1_P1_HOLD = 52393
    MESH_S3_N1_P1_QUENCH = 28039
    MESH_S3_N1_P2_SAMPLE = 1601
    MESH_S3_N1_P2_ARM = 17991
    MESH_S3_N1_P2_HOLD = 54014
    MESH_S3_N1_P2_QUENCH = 64122
    MESH_S3_N2_P0_SAMPLE = 49103
    MESH_S3_N2_P0_ARM = 35179
    MESH_S3_N2_P0_HOLD = 15660
    MESH_S3_N2_P0_QUENCH = 42310
    MESH_S3_N2_P1_SAMPLE = 28318
    MESH_S3_N2_P1_ARM = 43303
    MESH_S3_N2_P1_HOLD = 52403
    MESH_S3_N2_P1_QUENCH = 18890
    MESH_S3_N2_P2_SAMPLE = 39927
    MESH_S3_N2_P2_ARM = 12664
    MESH_S3_N2_P2_HOLD = 24479
    MESH_S3_N2_P2_QUENCH = 47207
    MESH_S3_N3_P0_SAMPLE = 33653
    MESH_S3_N3_P0_ARM = 18751
    MESH_S3_N3_P0_HOLD = 15531
    MESH_S3_N3_P0_QUENCH = 54835
    MESH_S3_N3_P1_SAMPLE = 36451
    MESH_S3_N3_P1_ARM = 45667
    MESH_S3_N3_P1_HOLD = 45742
    MESH_S3_N3_P1_QUENCH = 23599
    MESH_S3_N3_P2_SAMPLE = 3190
    MESH_S3_N3_P2_ARM = 2982
    MESH_S3_N3_P2_HOLD = 10684
    MESH_S3_N3_P2_QUENCH = 58748
    MESH_S4_N0_P0_SAMPLE = 15049
    MESH_S4_N0_P0_ARM = 13523
    MESH_S4_N0_P0_HOLD = 3394
    MESH_S4_N0_P0_QUENCH = 5641
    MESH_S4_N0_P1_SAMPLE = 13080
    MESH_S4_N0_P1_ARM = 7339
    MESH_S4_N0_P1_HOLD = 40715
    MESH_S4_N0_P1_QUENCH = 15903
    MESH_S4_N0_P2_SAMPLE = 7187
    MESH_S4_N0_P2_ARM = 23206
    MESH_S4_N0_P2_HOLD = 29435
    MESH_S4_N0_P2_QUENCH = 3380
    MESH_S4_N1_P0_SAMPLE = 37276
    MESH_S4_N1_P0_ARM = 56255
    MESH_S4_N1_P0_HOLD = 30003
    MESH_S4_N1_P0_QUENCH = 64950
    MESH_S4_N1_P1_SAMPLE = 59664
    MESH_S4_N1_P1_ARM = 181
    MESH_S4_N1_P1_HOLD = 1967
    MESH_S4_N1_P1_QUENCH = 43922
    MESH_S4_N1_P2_SAMPLE = 16686
    MESH_S4_N1_P2_ARM = 16352
    MESH_S4_N1_P2_HOLD = 60762
    MESH_S4_N1_P2_QUENCH = 63673
    MESH_S4_N2_P0_SAMPLE = 56030
    MESH_S4_N2_P0_ARM = 38659
    MESH_S4_N2_P0_HOLD = 41805
    MESH_S4_N2_P0_QUENCH = 51685
    MESH_S4_N2_P1_SAMPLE = 40375
    MESH_S4_N2_P1_ARM = 45902
    MESH_S4_N2_P1_HOLD = 9379
    MESH_S4_N2_P1_QUENCH = 19723
    MESH_S4_N2_P2_SAMPLE = 36871
    MESH_S4_N2_P2_ARM = 57727
    MESH_S4_N2_P2_HOLD = 16629
    MESH_S4_N2_P2_QUENCH = 32322
    MESH_S4_N3_P0_SAMPLE = 18467
    MESH_S4_N3_P0_ARM = 1371
    MESH_S4_N3_P0_HOLD = 23953
    MESH_S4_N3_P0_QUENCH = 24109
    MESH_S4_N3_P1_SAMPLE = 13964
    MESH_S4_N3_P1_ARM = 20932
    MESH_S4_N3_P1_HOLD = 20919
    MESH_S4_N3_P1_QUENCH = 15909
    MESH_S4_N3_P2_SAMPLE = 18063
    MESH_S4_N3_P2_ARM = 29131
    MESH_S4_N3_P2_HOLD = 53548
    MESH_S4_N3_P2_QUENCH = 65506
    MESH_S5_N0_P0_SAMPLE = 17318
    MESH_S5_N0_P0_ARM = 50517
    MESH_S5_N0_P0_HOLD = 48953
    MESH_S5_N0_P0_QUENCH = 48506
    MESH_S5_N0_P1_SAMPLE = 57631
    MESH_S5_N0_P1_ARM = 36402
    MESH_S5_N0_P1_HOLD = 30608
    MESH_S5_N0_P1_QUENCH = 3060
    MESH_S5_N0_P2_SAMPLE = 3488
    MESH_S5_N0_P2_ARM = 26939
    MESH_S5_N0_P2_HOLD = 18910
    MESH_S5_N0_P2_QUENCH = 21893
    MESH_S5_N1_P0_SAMPLE = 33705
    MESH_S5_N1_P0_ARM = 33309
    MESH_S5_N1_P0_HOLD = 40447
    MESH_S5_N1_P0_QUENCH = 30823
    MESH_S5_N1_P1_SAMPLE = 61559
    MESH_S5_N1_P1_ARM = 7866
    MESH_S5_N1_P1_HOLD = 15846
    MESH_S5_N1_P1_QUENCH = 45113
    MESH_S5_N1_P2_SAMPLE = 42223
    MESH_S5_N1_P2_ARM = 45541
    MESH_S5_N1_P2_HOLD = 1060
    MESH_S5_N1_P2_QUENCH = 26888
    MESH_S5_N2_P0_SAMPLE = 36713
    MESH_S5_N2_P0_ARM = 18611
    MESH_S5_N2_P0_HOLD = 65037
    MESH_S5_N2_P0_QUENCH = 51654
    MESH_S5_N2_P1_SAMPLE = 59103
    MESH_S5_N2_P1_ARM = 29582
    MESH_S5_N2_P1_HOLD = 41167
    MESH_S5_N2_P1_QUENCH = 58335
    MESH_S5_N2_P2_SAMPLE = 10040
    MESH_S5_N2_P2_ARM = 32682
    MESH_S5_N2_P2_HOLD = 5689
    MESH_S5_N2_P2_QUENCH = 14649
    MESH_S5_N3_P0_SAMPLE = 65136
    MESH_S5_N3_P0_ARM = 26468
    MESH_S5_N3_P0_HOLD = 31572
    MESH_S5_N3_P0_QUENCH = 61530
    MESH_S5_N3_P1_SAMPLE = 37786
    MESH_S5_N3_P1_ARM = 13712
    MESH_S5_N3_P1_HOLD = 50292
    MESH_S5_N3_P1_QUENCH = 62604
    MESH_S5_N3_P2_SAMPLE = 56862
    MESH_S5_N3_P2_ARM = 20579
    MESH_S5_N3_P2_HOLD = 18679
    MESH_S5_N3_P2_QUENCH = 18181
    BUS_LINK_STATE_PROBE = 40349
    BUS_LINK_STATE_PROBE2 = 11954
    BUS_RESERVE_EMERGENCY_HALT = 40000
    BUS_RESERVE_DIAGNOSTIC = 300
    BUS_RESERVE_AUDIT = 15505
    CENSUS = 48858




@dataclass(frozen=True)
class MeshS0N0P0SampleFinished:
    """`mesh.s0.n0.p0.sample` result carried by `finished` (0x20)."""

    uid: int


class _MeshS0N0P0Sample(TaskBinding):
    """report this probe's identity

    Schema path `mesh.s0.n0.p0.sample`, uid 37421.

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

    Schema path `mesh.s0.n0.p0.arm`, uid 45109.

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

    Schema path `mesh.s0.n0.p0.hold`, uid 44658.

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

    Schema path `mesh.s0.n0.p0.quench`, uid 8431.

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

    Schema path `mesh.s0.n0.p1.sample`, uid 23732.

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

    Schema path `mesh.s0.n0.p1.arm`, uid 17224.

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

    Schema path `mesh.s0.n0.p1.hold`, uid 20931.

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

    Schema path `mesh.s0.n0.p1.quench`, uid 10542.

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

    Schema path `mesh.s0.n0.p2.sample`, uid 41553.

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

    Schema path `mesh.s0.n0.p2.arm`, uid 51892.

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

    Schema path `mesh.s0.n0.p2.hold`, uid 46135.

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

    Schema path `mesh.s0.n0.p2.quench`, uid 15195.

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

    Schema path `mesh.s0.n1.p0.sample`, uid 36345.

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

    Schema path `mesh.s0.n1.p0.arm`, uid 28042.

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

    Schema path `mesh.s0.n1.p0.hold`, uid 12627.

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

    Schema path `mesh.s0.n1.p0.quench`, uid 35228.

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

    Schema path `mesh.s0.n1.p1.sample`, uid 54212.

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

    Schema path `mesh.s0.n1.p1.arm`, uid 13780.

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

    Schema path `mesh.s0.n1.p1.hold`, uid 53037.

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

    Schema path `mesh.s0.n1.p1.quench`, uid 56462.

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

    Schema path `mesh.s0.n1.p2.sample`, uid 3537.

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

    Schema path `mesh.s0.n1.p2.arm`, uid 37151.

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

    Schema path `mesh.s0.n1.p2.hold`, uid 38689.

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

    Schema path `mesh.s0.n1.p2.quench`, uid 59117.

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

    Schema path `mesh.s0.n2.p0.sample`, uid 44976.

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

    Schema path `mesh.s0.n2.p0.arm`, uid 55822.

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

    Schema path `mesh.s0.n2.p0.hold`, uid 47677.

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

    Schema path `mesh.s0.n2.p0.quench`, uid 11124.

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

    Schema path `mesh.s0.n2.p1.sample`, uid 19818.

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

    Schema path `mesh.s0.n2.p1.arm`, uid 63540.

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

    Schema path `mesh.s0.n2.p1.hold`, uid 10366.

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

    Schema path `mesh.s0.n2.p1.quench`, uid 18636.

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

    Schema path `mesh.s0.n2.p2.sample`, uid 11520.

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

    Schema path `mesh.s0.n2.p2.arm`, uid 46651.

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

    Schema path `mesh.s0.n2.p2.hold`, uid 12792.

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

    Schema path `mesh.s0.n2.p2.quench`, uid 22530.

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

    Schema path `mesh.s0.n3.p0.sample`, uid 11539.

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

    Schema path `mesh.s0.n3.p0.arm`, uid 47555.

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

    Schema path `mesh.s0.n3.p0.hold`, uid 12158.

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

    Schema path `mesh.s0.n3.p0.quench`, uid 486.

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

    Schema path `mesh.s0.n3.p1.sample`, uid 37186.

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

    Schema path `mesh.s0.n3.p1.arm`, uid 25458.

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

    Schema path `mesh.s0.n3.p1.hold`, uid 64765.

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

    Schema path `mesh.s0.n3.p1.quench`, uid 21537.

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

    Schema path `mesh.s0.n3.p2.sample`, uid 19705.

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

    Schema path `mesh.s0.n3.p2.arm`, uid 21311.

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

    Schema path `mesh.s0.n3.p2.hold`, uid 17048.

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

    Schema path `mesh.s0.n3.p2.quench`, uid 18608.

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

    Schema path `mesh.s1.n0.p0.sample`, uid 39285.

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

    Schema path `mesh.s1.n0.p0.arm`, uid 36249.

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

    Schema path `mesh.s1.n0.p0.hold`, uid 33267.

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

    Schema path `mesh.s1.n0.p0.quench`, uid 11006.

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

    Schema path `mesh.s1.n0.p1.sample`, uid 13509.

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

    Schema path `mesh.s1.n0.p1.arm`, uid 29029.

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

    Schema path `mesh.s1.n0.p1.hold`, uid 61501.

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

    Schema path `mesh.s1.n0.p1.quench`, uid 28716.

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

    Schema path `mesh.s1.n0.p2.sample`, uid 14900.

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

    Schema path `mesh.s1.n0.p2.arm`, uid 3269.

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

    Schema path `mesh.s1.n0.p2.hold`, uid 41765.

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

    Schema path `mesh.s1.n0.p2.quench`, uid 41938.

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

    Schema path `mesh.s1.n1.p0.sample`, uid 14964.

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

    Schema path `mesh.s1.n1.p0.arm`, uid 28124.

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

    Schema path `mesh.s1.n1.p0.hold`, uid 53812.

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

    Schema path `mesh.s1.n1.p0.quench`, uid 15193.

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

    Schema path `mesh.s1.n1.p1.sample`, uid 18632.

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

    Schema path `mesh.s1.n1.p1.arm`, uid 55432.

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

    Schema path `mesh.s1.n1.p1.hold`, uid 64454.

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

    Schema path `mesh.s1.n1.p1.quench`, uid 53130.

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

    Schema path `mesh.s1.n1.p2.sample`, uid 34045.

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

    Schema path `mesh.s1.n1.p2.arm`, uid 60443.

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

    Schema path `mesh.s1.n1.p2.hold`, uid 24811.

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

    Schema path `mesh.s1.n1.p2.quench`, uid 17486.

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

    Schema path `mesh.s1.n2.p0.sample`, uid 59804.

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

    Schema path `mesh.s1.n2.p0.arm`, uid 60970.

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

    Schema path `mesh.s1.n2.p0.hold`, uid 38423.

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

    Schema path `mesh.s1.n2.p0.quench`, uid 46512.

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

    Schema path `mesh.s1.n2.p1.sample`, uid 60332.

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

    Schema path `mesh.s1.n2.p1.arm`, uid 40602.

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

    Schema path `mesh.s1.n2.p1.hold`, uid 50904.

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

    Schema path `mesh.s1.n2.p1.quench`, uid 27821.

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

    Schema path `mesh.s1.n2.p2.sample`, uid 4308.

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

    Schema path `mesh.s1.n2.p2.arm`, uid 27846.

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

    Schema path `mesh.s1.n2.p2.hold`, uid 64056.

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

    Schema path `mesh.s1.n2.p2.quench`, uid 43450.

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

    Schema path `mesh.s1.n3.p0.sample`, uid 59666.

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

    Schema path `mesh.s1.n3.p0.arm`, uid 48490.

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

    Schema path `mesh.s1.n3.p0.hold`, uid 61198.

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

    Schema path `mesh.s1.n3.p0.quench`, uid 37161.

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

    Schema path `mesh.s1.n3.p1.sample`, uid 29865.

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

    Schema path `mesh.s1.n3.p1.arm`, uid 18401.

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

    Schema path `mesh.s1.n3.p1.hold`, uid 48947.

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

    Schema path `mesh.s1.n3.p1.quench`, uid 697.

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

    Schema path `mesh.s1.n3.p2.sample`, uid 40532.

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

    Schema path `mesh.s1.n3.p2.arm`, uid 3887.

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

    Schema path `mesh.s1.n3.p2.hold`, uid 1920.

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

    Schema path `mesh.s1.n3.p2.quench`, uid 28640.

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

    Schema path `mesh.s2.n0.p0.sample`, uid 30090.

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

    Schema path `mesh.s2.n0.p0.arm`, uid 34650.

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

    Schema path `mesh.s2.n0.p0.hold`, uid 39322.

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

    Schema path `mesh.s2.n0.p0.quench`, uid 9783.

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

    Schema path `mesh.s2.n0.p1.sample`, uid 32908.

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

    Schema path `mesh.s2.n0.p1.arm`, uid 2107.

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

    Schema path `mesh.s2.n0.p1.hold`, uid 49512.

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

    Schema path `mesh.s2.n0.p1.quench`, uid 16300.

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

    Schema path `mesh.s2.n0.p2.sample`, uid 35088.

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

    Schema path `mesh.s2.n0.p2.arm`, uid 44755.

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

    Schema path `mesh.s2.n0.p2.hold`, uid 7183.

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

    Schema path `mesh.s2.n0.p2.quench`, uid 7056.

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

    Schema path `mesh.s2.n1.p0.sample`, uid 43294.

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

    Schema path `mesh.s2.n1.p0.arm`, uid 22674.

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

    Schema path `mesh.s2.n1.p0.hold`, uid 55171.

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

    Schema path `mesh.s2.n1.p0.quench`, uid 17050.

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

    Schema path `mesh.s2.n1.p1.sample`, uid 42707.

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

    Schema path `mesh.s2.n1.p1.arm`, uid 53214.

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

    Schema path `mesh.s2.n1.p1.hold`, uid 28474.

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

    Schema path `mesh.s2.n1.p1.quench`, uid 23054.

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

    Schema path `mesh.s2.n1.p2.sample`, uid 38556.

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

    Schema path `mesh.s2.n1.p2.arm`, uid 38282.

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

    Schema path `mesh.s2.n1.p2.hold`, uid 9839.

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

    Schema path `mesh.s2.n1.p2.quench`, uid 21148.

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

    Schema path `mesh.s2.n2.p0.sample`, uid 9603.

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

    Schema path `mesh.s2.n2.p0.arm`, uid 30738.

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

    Schema path `mesh.s2.n2.p0.hold`, uid 44390.

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

    Schema path `mesh.s2.n2.p0.quench`, uid 24899.

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

    Schema path `mesh.s2.n2.p1.sample`, uid 21164.

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

    Schema path `mesh.s2.n2.p1.arm`, uid 22989.

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

    Schema path `mesh.s2.n2.p1.hold`, uid 39829.

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

    Schema path `mesh.s2.n2.p1.quench`, uid 30781.

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

    Schema path `mesh.s2.n2.p2.sample`, uid 40098.

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

    Schema path `mesh.s2.n2.p2.arm`, uid 35484.

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

    Schema path `mesh.s2.n2.p2.hold`, uid 6195.

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

    Schema path `mesh.s2.n2.p2.quench`, uid 4742.

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

    Schema path `mesh.s2.n3.p0.sample`, uid 21361.

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

    Schema path `mesh.s2.n3.p0.arm`, uid 31697.

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

    Schema path `mesh.s2.n3.p0.hold`, uid 14457.

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

    Schema path `mesh.s2.n3.p0.quench`, uid 16594.

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

    Schema path `mesh.s2.n3.p1.sample`, uid 35769.

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

    Schema path `mesh.s2.n3.p1.arm`, uid 5767.

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

    Schema path `mesh.s2.n3.p1.hold`, uid 7506.

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

    Schema path `mesh.s2.n3.p1.quench`, uid 21867.

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

    Schema path `mesh.s2.n3.p2.sample`, uid 9159.

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

    Schema path `mesh.s2.n3.p2.arm`, uid 12356.

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

    Schema path `mesh.s2.n3.p2.hold`, uid 42930.

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

    Schema path `mesh.s2.n3.p2.quench`, uid 33575.

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

    Schema path `mesh.s3.n0.p0.sample`, uid 28690.

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

    Schema path `mesh.s3.n0.p0.arm`, uid 57576.

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

    Schema path `mesh.s3.n0.p0.hold`, uid 28066.

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

    Schema path `mesh.s3.n0.p0.quench`, uid 6511.

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

    Schema path `mesh.s3.n0.p1.sample`, uid 55179.

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

    Schema path `mesh.s3.n0.p1.arm`, uid 56848.

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

    Schema path `mesh.s3.n0.p1.hold`, uid 1600.

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

    Schema path `mesh.s3.n0.p1.quench`, uid 19856.

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

    Schema path `mesh.s3.n0.p2.sample`, uid 33782.

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

    Schema path `mesh.s3.n0.p2.arm`, uid 36305.

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

    Schema path `mesh.s3.n0.p2.hold`, uid 21338.

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

    Schema path `mesh.s3.n0.p2.quench`, uid 20582.

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

    Schema path `mesh.s3.n1.p0.sample`, uid 44344.

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

    Schema path `mesh.s3.n1.p0.arm`, uid 39787.

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

    Schema path `mesh.s3.n1.p0.hold`, uid 44506.

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

    Schema path `mesh.s3.n1.p0.quench`, uid 51792.

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

    Schema path `mesh.s3.n1.p1.sample`, uid 59806.

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

    Schema path `mesh.s3.n1.p1.arm`, uid 48391.

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

    Schema path `mesh.s3.n1.p1.hold`, uid 52393.

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

    Schema path `mesh.s3.n1.p1.quench`, uid 28039.

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

    Schema path `mesh.s3.n1.p2.sample`, uid 1601.

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

    Schema path `mesh.s3.n1.p2.arm`, uid 17991.

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

    Schema path `mesh.s3.n1.p2.hold`, uid 54014.

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

    Schema path `mesh.s3.n1.p2.quench`, uid 64122.

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

    Schema path `mesh.s3.n2.p0.sample`, uid 49103.

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

    Schema path `mesh.s3.n2.p0.arm`, uid 35179.

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

    Schema path `mesh.s3.n2.p0.hold`, uid 15660.

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

    Schema path `mesh.s3.n2.p0.quench`, uid 42310.

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

    Schema path `mesh.s3.n2.p1.sample`, uid 28318.

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

    Schema path `mesh.s3.n2.p1.arm`, uid 43303.

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

    Schema path `mesh.s3.n2.p1.hold`, uid 52403.

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

    Schema path `mesh.s3.n2.p1.quench`, uid 18890.

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

    Schema path `mesh.s3.n2.p2.sample`, uid 39927.

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

    Schema path `mesh.s3.n2.p2.arm`, uid 12664.

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

    Schema path `mesh.s3.n2.p2.hold`, uid 24479.

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

    Schema path `mesh.s3.n2.p2.quench`, uid 47207.

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

    Schema path `mesh.s3.n3.p0.sample`, uid 33653.

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

    Schema path `mesh.s3.n3.p0.arm`, uid 18751.

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

    Schema path `mesh.s3.n3.p0.hold`, uid 15531.

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

    Schema path `mesh.s3.n3.p0.quench`, uid 54835.

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

    Schema path `mesh.s3.n3.p1.sample`, uid 36451.

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

    Schema path `mesh.s3.n3.p1.arm`, uid 45667.

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

    Schema path `mesh.s3.n3.p1.hold`, uid 45742.

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

    Schema path `mesh.s3.n3.p1.quench`, uid 23599.

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

    Schema path `mesh.s3.n3.p2.sample`, uid 3190.

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

    Schema path `mesh.s3.n3.p2.arm`, uid 2982.

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

    Schema path `mesh.s3.n3.p2.hold`, uid 10684.

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

    Schema path `mesh.s3.n3.p2.quench`, uid 58748.

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

    Schema path `mesh.s4.n0.p0.sample`, uid 15049.

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

    Schema path `mesh.s4.n0.p0.arm`, uid 13523.

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

    Schema path `mesh.s4.n0.p0.hold`, uid 3394.

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

    Schema path `mesh.s4.n0.p0.quench`, uid 5641.

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

    Schema path `mesh.s4.n0.p1.sample`, uid 13080.

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

    Schema path `mesh.s4.n0.p1.arm`, uid 7339.

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

    Schema path `mesh.s4.n0.p1.hold`, uid 40715.

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

    Schema path `mesh.s4.n0.p1.quench`, uid 15903.

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

    Schema path `mesh.s4.n0.p2.sample`, uid 7187.

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

    Schema path `mesh.s4.n0.p2.arm`, uid 23206.

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

    Schema path `mesh.s4.n0.p2.hold`, uid 29435.

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

    Schema path `mesh.s4.n0.p2.quench`, uid 3380.

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

    Schema path `mesh.s4.n1.p0.sample`, uid 37276.

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

    Schema path `mesh.s4.n1.p0.arm`, uid 56255.

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

    Schema path `mesh.s4.n1.p0.hold`, uid 30003.

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

    Schema path `mesh.s4.n1.p0.quench`, uid 64950.

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

    Schema path `mesh.s4.n1.p1.sample`, uid 59664.

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

    Schema path `mesh.s4.n1.p1.arm`, uid 181.

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

    Schema path `mesh.s4.n1.p1.hold`, uid 1967.

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

    Schema path `mesh.s4.n1.p1.quench`, uid 43922.

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

    Schema path `mesh.s4.n1.p2.sample`, uid 16686.

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

    Schema path `mesh.s4.n1.p2.arm`, uid 16352.

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

    Schema path `mesh.s4.n1.p2.hold`, uid 60762.

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

    Schema path `mesh.s4.n1.p2.quench`, uid 63673.

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

    Schema path `mesh.s4.n2.p0.sample`, uid 56030.

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

    Schema path `mesh.s4.n2.p0.arm`, uid 38659.

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

    Schema path `mesh.s4.n2.p0.hold`, uid 41805.

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

    Schema path `mesh.s4.n2.p0.quench`, uid 51685.

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

    Schema path `mesh.s4.n2.p1.sample`, uid 40375.

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

    Schema path `mesh.s4.n2.p1.arm`, uid 45902.

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

    Schema path `mesh.s4.n2.p1.hold`, uid 9379.

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

    Schema path `mesh.s4.n2.p1.quench`, uid 19723.

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

    Schema path `mesh.s4.n2.p2.sample`, uid 36871.

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

    Schema path `mesh.s4.n2.p2.arm`, uid 57727.

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

    Schema path `mesh.s4.n2.p2.hold`, uid 16629.

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

    Schema path `mesh.s4.n2.p2.quench`, uid 32322.

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

    Schema path `mesh.s4.n3.p0.sample`, uid 18467.

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

    Schema path `mesh.s4.n3.p0.arm`, uid 1371.

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

    Schema path `mesh.s4.n3.p0.hold`, uid 23953.

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

    Schema path `mesh.s4.n3.p0.quench`, uid 24109.

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

    Schema path `mesh.s4.n3.p1.sample`, uid 13964.

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

    Schema path `mesh.s4.n3.p1.arm`, uid 20932.

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

    Schema path `mesh.s4.n3.p1.hold`, uid 20919.

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

    Schema path `mesh.s4.n3.p1.quench`, uid 15909.

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

    Schema path `mesh.s4.n3.p2.sample`, uid 18063.

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

    Schema path `mesh.s4.n3.p2.arm`, uid 29131.

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

    Schema path `mesh.s4.n3.p2.hold`, uid 53548.

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

    Schema path `mesh.s4.n3.p2.quench`, uid 65506.

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

    Schema path `mesh.s5.n0.p0.sample`, uid 17318.

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

    Schema path `mesh.s5.n0.p0.arm`, uid 50517.

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

    Schema path `mesh.s5.n0.p0.hold`, uid 48953.

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

    Schema path `mesh.s5.n0.p0.quench`, uid 48506.

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

    Schema path `mesh.s5.n0.p1.sample`, uid 57631.

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

    Schema path `mesh.s5.n0.p1.arm`, uid 36402.

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

    Schema path `mesh.s5.n0.p1.hold`, uid 30608.

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

    Schema path `mesh.s5.n0.p1.quench`, uid 3060.

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

    Schema path `mesh.s5.n0.p2.sample`, uid 3488.

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

    Schema path `mesh.s5.n0.p2.arm`, uid 26939.

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

    Schema path `mesh.s5.n0.p2.hold`, uid 18910.

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

    Schema path `mesh.s5.n0.p2.quench`, uid 21893.

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

    Schema path `mesh.s5.n1.p0.sample`, uid 33705.

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

    Schema path `mesh.s5.n1.p0.arm`, uid 33309.

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

    Schema path `mesh.s5.n1.p0.hold`, uid 40447.

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

    Schema path `mesh.s5.n1.p0.quench`, uid 30823.

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

    Schema path `mesh.s5.n1.p1.sample`, uid 61559.

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

    Schema path `mesh.s5.n1.p1.arm`, uid 7866.

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

    Schema path `mesh.s5.n1.p1.hold`, uid 15846.

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

    Schema path `mesh.s5.n1.p1.quench`, uid 45113.

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

    Schema path `mesh.s5.n1.p2.sample`, uid 42223.

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

    Schema path `mesh.s5.n1.p2.arm`, uid 45541.

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

    Schema path `mesh.s5.n1.p2.hold`, uid 1060.

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

    Schema path `mesh.s5.n1.p2.quench`, uid 26888.

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

    Schema path `mesh.s5.n2.p0.sample`, uid 36713.

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

    Schema path `mesh.s5.n2.p0.arm`, uid 18611.

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

    Schema path `mesh.s5.n2.p0.hold`, uid 65037.

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

    Schema path `mesh.s5.n2.p0.quench`, uid 51654.

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

    Schema path `mesh.s5.n2.p1.sample`, uid 59103.

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

    Schema path `mesh.s5.n2.p1.arm`, uid 29582.

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

    Schema path `mesh.s5.n2.p1.hold`, uid 41167.

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

    Schema path `mesh.s5.n2.p1.quench`, uid 58335.

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

    Schema path `mesh.s5.n2.p2.sample`, uid 10040.

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

    Schema path `mesh.s5.n2.p2.arm`, uid 32682.

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

    Schema path `mesh.s5.n2.p2.hold`, uid 5689.

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

    Schema path `mesh.s5.n2.p2.quench`, uid 14649.

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

    Schema path `mesh.s5.n3.p0.sample`, uid 65136.

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

    Schema path `mesh.s5.n3.p0.arm`, uid 26468.

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

    Schema path `mesh.s5.n3.p0.hold`, uid 31572.

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

    Schema path `mesh.s5.n3.p0.quench`, uid 61530.

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

    Schema path `mesh.s5.n3.p1.sample`, uid 37786.

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

    Schema path `mesh.s5.n3.p1.arm`, uid 13712.

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

    Schema path `mesh.s5.n3.p1.hold`, uid 50292.

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

    Schema path `mesh.s5.n3.p1.quench`, uid 62604.

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

    Schema path `mesh.s5.n3.p2.sample`, uid 56862.

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

    Schema path `mesh.s5.n3.p2.arm`, uid 20579.

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

    Schema path `mesh.s5.n3.p2.hold`, uid 18679.

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

    Schema path `mesh.s5.n3.p2.quench`, uid 18181.

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

    Schema path `bus.link_state.probe`, uid 40349.

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

    Schema path `bus.link.state_probe2`, uid 11954.

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
    """pinned high - halt everything

    Schema path `bus.reserve.emergency_halt`, uid 40000.

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
    """pinned low - report this task's identity

    Schema path `bus.reserve.diagnostic`, uid 300.

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
    """derived, among pinned siblings

    Schema path `bus.reserve.audit`, uid 15505.

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

    Schema path `census`, uid 48858.

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
    """tasks holding pinned, explicit uids

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
