"""Generated etask client bindings - do not edit.

Regenerated from the project's schema on every `python -m schemav2.cli
generate --python` run; 12 task(s).

Each task is an awaitable call whose result is one of its declared
shapes, chosen by the status code the reply carries::

    async with Client(channel, uid_bytes=UID_BYTES) as client:
        tasks = Tasks(client)
        result = await tasks.<scope>.<task>(<params>)

Launching does not block: start several tasks and await them together
with `asyncio.gather`. See `etask.client` for how replies are matched.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from etask.binding import Scope, TaskBinding, UndeclaredResult, build_shapes
from etask.client import Client

UID_BYTES = 1
"""Width of a task uid on the wire, pinned by the project's uid ledger."""


class TaskId(IntEnum):
    """Every task's wire uid - the same values as `global::task_id` in C++."""

    HEAD_IMU_READ = 85
    ARMS_LEFT_MOVE_TO = 123
    ARMS_LEFT_STOP = 129
    ARMS_LEFT_GRASP = 24
    ARMS_RIGHT_MOVE_TO = 102
    ARMS_RIGHT_STOP = 151
    ARMS_RIGHT_GRASP = 86
    LEGS_LEFT_STEP = 109
    LEGS_LEFT_STOP = 41
    LEGS_RIGHT_STEP = 180
    LEGS_RIGHT_STOP = 18
    REBOOT = 255




@dataclass(frozen=True)
class HeadImuReadFinished:
    """`head.imu.read` result carried by `finished` (0x20)."""

    ax: float
    ay: float
    az: float


class _HeadImuRead(TaskBinding):
    """sample the accelerometer

    Schema path `head.imu.read`, uid 85.

    Returns one of:
      - `HeadImuReadFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.HEAD_IMU_READ
    PATH = "head.imu.read"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, HeadImuReadFinished, ("float", "float", "float")),
    ])

    Finished = HeadImuReadFinished

    async def __call__(self) -> HeadImuReadFinished | UndeclaredResult:
        """Starts `head.imu.read` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class ArmsLeftMoveToFinished:
    """`arms.left.move_to` result carried by `finished` (0x20)."""

    reached: bool


class _ArmsLeftMoveTo(TaskBinding):
    """move the hand to a target pose

    Schema path `arms.left.move_to`, uid 123.

    Returns one of:
      - `ArmsLeftMoveToFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ARMS_LEFT_MOVE_TO
    PATH = "arms.left.move_to"
    PARAMS = ("float", "float", "float", "uint8")
    SHAPES = build_shapes([
        (0x20, ArmsLeftMoveToFinished, ("bool",)),
    ])

    Finished = ArmsLeftMoveToFinished

    async def __call__(self, *, x: float, y: float, z: float, speed: int) -> ArmsLeftMoveToFinished | UndeclaredResult:
        """Starts `arms.left.move_to` and waits for its reply.

        Args:
            x: `float`.
            y: `float`.
            z: `float`.
            speed: `uint8`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([x, y, z, speed])


class _ArmsLeftStop(TaskBinding):
    """halt the arm immediately

    Schema path `arms.left.stop`, uid 129.
    """

    UID = TaskId.ARMS_LEFT_STOP
    PATH = "arms.left.stop"
    PARAMS = ()
    SHAPES = {}

    async def __call__(self) -> UndeclaredResult:
        """Starts `arms.left.stop` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class ArmsLeftGraspFinished:
    """`arms.left.grasp` result carried by `finished` (0x20)."""

    v0: int
    v1: float


class _ArmsLeftGrasp(TaskBinding):
    """close the gripper until a force threshold

    Schema path `arms.left.grasp`, uid 24.

    Returns one of:
      - `ArmsLeftGraspFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ARMS_LEFT_GRASP
    PATH = "arms.left.grasp"
    PARAMS = ("uint16", "uint32")
    SHAPES = build_shapes([
        (0x20, ArmsLeftGraspFinished, ("uint8", "float")),
    ])

    Finished = ArmsLeftGraspFinished

    async def __call__(self, *, force: int, timeout_ms: int) -> ArmsLeftGraspFinished | UndeclaredResult:
        """Starts `arms.left.grasp` and waits for its reply.

        Args:
            force: `uint16`.
            timeout_ms: `uint32`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([force, timeout_ms])


@dataclass(frozen=True)
class ArmsRightMoveToFinished:
    """`arms.right.move_to` result carried by `finished` (0x20)."""

    reached: bool


class _ArmsRightMoveTo(TaskBinding):
    """move the hand to a target pose

    Schema path `arms.right.move_to`, uid 102.

    Returns one of:
      - `ArmsRightMoveToFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ARMS_RIGHT_MOVE_TO
    PATH = "arms.right.move_to"
    PARAMS = ("float", "float", "float", "uint8")
    SHAPES = build_shapes([
        (0x20, ArmsRightMoveToFinished, ("bool",)),
    ])

    Finished = ArmsRightMoveToFinished

    async def __call__(self, *, x: float, y: float, z: float, speed: int) -> ArmsRightMoveToFinished | UndeclaredResult:
        """Starts `arms.right.move_to` and waits for its reply.

        Args:
            x: `float`.
            y: `float`.
            z: `float`.
            speed: `uint8`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([x, y, z, speed])


class _ArmsRightStop(TaskBinding):
    """halt the arm immediately

    Schema path `arms.right.stop`, uid 151.
    """

    UID = TaskId.ARMS_RIGHT_STOP
    PATH = "arms.right.stop"
    PARAMS = ()
    SHAPES = {}

    async def __call__(self) -> UndeclaredResult:
        """Starts `arms.right.stop` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class ArmsRightGraspFinished:
    """`arms.right.grasp` result carried by `finished` (0x20)."""

    v0: int
    v1: float


class _ArmsRightGrasp(TaskBinding):
    """close the gripper until a force threshold

    Schema path `arms.right.grasp`, uid 86.

    Returns one of:
      - `ArmsRightGraspFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.ARMS_RIGHT_GRASP
    PATH = "arms.right.grasp"
    PARAMS = ("uint16", "uint32")
    SHAPES = build_shapes([
        (0x20, ArmsRightGraspFinished, ("uint8", "float")),
    ])

    Finished = ArmsRightGraspFinished

    async def __call__(self, *, force: int, timeout_ms: int) -> ArmsRightGraspFinished | UndeclaredResult:
        """Starts `arms.right.grasp` and waits for its reply.

        Args:
            force: `uint16`.
            timeout_ms: `uint32`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([force, timeout_ms])


@dataclass(frozen=True)
class LegsLeftStepFinished:
    """`legs.left.step` result carried by `finished` (0x20)."""

    stable: bool


class _LegsLeftStep(TaskBinding):
    """take one step

    Schema path `legs.left.step`, uid 109.

    Returns one of:
      - `LegsLeftStepFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.LEGS_LEFT_STEP
    PATH = "legs.left.step"
    PARAMS = ("float", "uint8")
    SHAPES = build_shapes([
        (0x20, LegsLeftStepFinished, ("bool",)),
    ])

    Finished = LegsLeftStepFinished

    async def __call__(self, *, stride: float, speed: int) -> LegsLeftStepFinished | UndeclaredResult:
        """Starts `legs.left.step` and waits for its reply.

        Args:
            stride: `float`.
            speed: `uint8`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([stride, speed])


class _LegsLeftStop(TaskBinding):
    """plant the foot and hold

    Schema path `legs.left.stop`, uid 41.
    """

    UID = TaskId.LEGS_LEFT_STOP
    PATH = "legs.left.stop"
    PARAMS = ()
    SHAPES = {}

    async def __call__(self) -> UndeclaredResult:
        """Starts `legs.left.stop` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class LegsRightStepFinished:
    """`legs.right.step` result carried by `finished` (0x20)."""

    stable: bool


class _LegsRightStep(TaskBinding):
    """take one step

    Schema path `legs.right.step`, uid 180.

    Returns one of:
      - `LegsRightStepFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.LEGS_RIGHT_STEP
    PATH = "legs.right.step"
    PARAMS = ("float", "uint8")
    SHAPES = build_shapes([
        (0x20, LegsRightStepFinished, ("bool",)),
    ])

    Finished = LegsRightStepFinished

    async def __call__(self, *, stride: float, speed: int) -> LegsRightStepFinished | UndeclaredResult:
        """Starts `legs.right.step` and waits for its reply.

        Args:
            stride: `float`.
            speed: `uint8`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([stride, speed])


class _LegsRightStop(TaskBinding):
    """plant the foot and hold

    Schema path `legs.right.stop`, uid 18.
    """

    UID = TaskId.LEGS_RIGHT_STOP
    PATH = "legs.right.stop"
    PARAMS = ()
    SHAPES = {}

    async def __call__(self) -> UndeclaredResult:
        """Starts `legs.right.stop` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _Reboot(TaskBinding):
    """reboot the controller

    Schema path `reboot`, uid 255.
    """

    UID = TaskId.REBOOT
    PATH = "reboot"
    PARAMS = ()
    SHAPES = {}

    async def __call__(self) -> UndeclaredResult:
        """Starts `reboot` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _LegsRightScope(Scope):
    """a leg

    Schema scope `legs.right`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.step = _LegsRightStep(client)
        self.stop = _LegsRightStop(client)


class _LegsLeftScope(Scope):
    """a leg

    Schema scope `legs.left`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.step = _LegsLeftStep(client)
        self.stop = _LegsLeftStop(client)


class _LegsScope(Scope):
    """the two legs

    Schema scope `legs`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.left = _LegsLeftScope(client)
        self.right = _LegsRightScope(client)


class _ArmsRightScope(Scope):
    """an articulated arm with a gripper

    Schema scope `arms.right`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.move_to = _ArmsRightMoveTo(client)
        self.stop = _ArmsRightStop(client)
        self.grasp = _ArmsRightGrasp(client)


class _ArmsLeftScope(Scope):
    """an articulated arm with a gripper

    Schema scope `arms.left`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.move_to = _ArmsLeftMoveTo(client)
        self.stop = _ArmsLeftStop(client)
        self.grasp = _ArmsLeftGrasp(client)


class _ArmsScope(Scope):
    """the two arms

    Schema scope `arms`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.left = _ArmsLeftScope(client)
        self.right = _ArmsRightScope(client)


class _HeadImuScope(Scope):
    """inertial measurement unit

    Schema scope `head.imu`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.read = _HeadImuRead(client)


class _HeadScope(Scope):
    """sensor head

    Schema scope `head`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.imu = _HeadImuScope(client)


class Tasks(Scope):
    """The project's task tree, mirroring the schema's scopes.

    Construct it with a live `Client`; every task below is an
    awaitable call at the same path the schema declares.
    """

    UID_BYTES = UID_BYTES

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.head = _HeadScope(client)
        self.arms = _ArmsScope(client)
        self.legs = _LegsScope(client)
        self.reboot = _Reboot(client)
