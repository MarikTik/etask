"""Generated etask client bindings - do not edit.

Regenerated from the project's schema on every `etask generate --python`
run; 15 task(s).

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

from etask.binding import (
    InstantTaskBinding,
    Scope,
    TaskBinding,
    UndeclaredResult,
    build_shapes,
)
from etask.client import Client

UID_BYTES = 1
"""Width of a task uid on the wire, pinned by the project's uid ledger."""


class TaskId(IntEnum):
    """Every task's wire uid - the same values as `global::task_id` in C++."""

    ROTORS_FL_SET_THRUST = 139
    ROTORS_FL_STOP = 223
    ROTORS_FR_SET_THRUST = 35
    ROTORS_FR_STOP = 141
    ROTORS_RL_SET_THRUST = 51
    ROTORS_RL_STOP = 239
    ROTORS_RR_SET_THRUST = 42
    ROTORS_RR_STOP = 157
    SENSORS_IMU_READ = 84
    SENSORS_BARO_READ_ALTITUDE = 18
    SENSORS_GPS_FIX = 29
    NAV_FLY_TO = 16
    NAV_HOLD = 243
    NAV_LAND = 41
    FAILSAFE = 255




class _RotorsFlSetThrust(TaskBinding):
    """drive this rotor to a thrust level

    Schema path `rotors.fl.set_thrust`, uid 139.
    """

    UID = TaskId.ROTORS_FL_SET_THRUST
    PATH = "rotors.fl.set_thrust"
    PARAMS = ("float",)
    SHAPES = {}

    async def __call__(self, *, level: float) -> UndeclaredResult:
        """Starts `rotors.fl.set_thrust` and waits for its reply.

        Args:
            level: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([level])


class _RotorsFlStop(InstantTaskBinding):
    """cut this rotor immediately

    Schema path `rotors.fl.stop`, uid 223.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.ROTORS_FL_STOP
    PATH = "rotors.fl.stop"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `rotors.fl.stop` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


class _RotorsFrSetThrust(TaskBinding):
    """drive this rotor to a thrust level

    Schema path `rotors.fr.set_thrust`, uid 35.
    """

    UID = TaskId.ROTORS_FR_SET_THRUST
    PATH = "rotors.fr.set_thrust"
    PARAMS = ("float",)
    SHAPES = {}

    async def __call__(self, *, level: float) -> UndeclaredResult:
        """Starts `rotors.fr.set_thrust` and waits for its reply.

        Args:
            level: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([level])


class _RotorsFrStop(InstantTaskBinding):
    """cut this rotor immediately

    Schema path `rotors.fr.stop`, uid 141.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.ROTORS_FR_STOP
    PATH = "rotors.fr.stop"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `rotors.fr.stop` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


class _RotorsRlSetThrust(TaskBinding):
    """drive this rotor to a thrust level

    Schema path `rotors.rl.set_thrust`, uid 51.
    """

    UID = TaskId.ROTORS_RL_SET_THRUST
    PATH = "rotors.rl.set_thrust"
    PARAMS = ("float",)
    SHAPES = {}

    async def __call__(self, *, level: float) -> UndeclaredResult:
        """Starts `rotors.rl.set_thrust` and waits for its reply.

        Args:
            level: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([level])


class _RotorsRlStop(InstantTaskBinding):
    """cut this rotor immediately

    Schema path `rotors.rl.stop`, uid 239.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.ROTORS_RL_STOP
    PATH = "rotors.rl.stop"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `rotors.rl.stop` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


class _RotorsRrSetThrust(TaskBinding):
    """drive this rotor to a thrust level

    Schema path `rotors.rr.set_thrust`, uid 42.
    """

    UID = TaskId.ROTORS_RR_SET_THRUST
    PATH = "rotors.rr.set_thrust"
    PARAMS = ("float",)
    SHAPES = {}

    async def __call__(self, *, level: float) -> UndeclaredResult:
        """Starts `rotors.rr.set_thrust` and waits for its reply.

        Args:
            level: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([level])


class _RotorsRrStop(InstantTaskBinding):
    """cut this rotor immediately

    Schema path `rotors.rr.stop`, uid 157.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.ROTORS_RR_STOP
    PATH = "rotors.rr.stop"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `rotors.rr.stop` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


@dataclass(frozen=True)
class SensorsImuReadFinished:
    """`sensors.imu.read` result carried by `finished` (0x20)."""

    ax: float
    ay: float
    az: float
    gx: float
    gy: float
    gz: float


class _SensorsImuRead(TaskBinding):
    """sample accel + gyro

    Schema path `sensors.imu.read`, uid 84.

    Returns one of:
      - `SensorsImuReadFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.SENSORS_IMU_READ
    PATH = "sensors.imu.read"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, SensorsImuReadFinished, ("float", "float", "float", "float", "float", "float")),
    ])

    Finished = SensorsImuReadFinished

    async def __call__(self) -> SensorsImuReadFinished | UndeclaredResult:
        """Starts `sensors.imu.read` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class SensorsBaroReadAltitudeFinished:
    """`sensors.baro.read_altitude` result carried by `finished` (0x20)."""

    meters: float


class _SensorsBaroReadAltitude(TaskBinding):
    """read altitude above the launch point

    Schema path `sensors.baro.read_altitude`, uid 18.

    Returns one of:
      - `SensorsBaroReadAltitudeFinished` on `finished` (0x20)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.SENSORS_BARO_READ_ALTITUDE
    PATH = "sensors.baro.read_altitude"
    PARAMS = ()
    SHAPES = build_shapes([
        (0x20, SensorsBaroReadAltitudeFinished, ("float",)),
    ])

    Finished = SensorsBaroReadAltitudeFinished

    async def __call__(self) -> SensorsBaroReadAltitudeFinished | UndeclaredResult:
        """Starts `sensors.baro.read_altitude` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


@dataclass(frozen=True)
class SensorsGpsFixFinished:
    """`sensors.gps.fix` result carried by `finished` (0x20)."""

    lat: float
    lon: float
    sats: int


@dataclass(frozen=True)
class SensorsGpsFixTimeout:
    """`sensors.gps.fix` result carried by `task_timeout` (0x22)."""

    waited_ms: int
    sats_seen: int


class _SensorsGpsFix(TaskBinding):
    """acquire a position fix

    Schema path `sensors.gps.fix`, uid 29.

    Returns one of:
      - `SensorsGpsFixFinished` on `finished` (0x20)
      - `SensorsGpsFixTimeout` on `task_timeout` (0x22)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.SENSORS_GPS_FIX
    PATH = "sensors.gps.fix"
    PARAMS = ("uint32",)
    SHAPES = build_shapes([
        (0x20, SensorsGpsFixFinished, ("double", "double", "uint8")),
        (0x22, SensorsGpsFixTimeout, ("uint32", "uint8")),
    ])

    Finished = SensorsGpsFixFinished
    Timeout = SensorsGpsFixTimeout

    async def __call__(self, *, timeout_ms: int) -> SensorsGpsFixFinished | SensorsGpsFixTimeout | UndeclaredResult:
        """Starts `sensors.gps.fix` and waits for its reply.

        Args:
            timeout_ms: `uint32`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([timeout_ms])


@dataclass(frozen=True)
class NavFlyToFinished:
    """`nav.fly_to` result carried by `finished` (0x20)."""

    flight_time_s: int


@dataclass(frozen=True)
class NavFlyToAborted:
    """`nav.fly_to` result carried by `aborted` (0x21)."""

    lat: float
    lon: float
    alt: float


@dataclass(frozen=True)
class NavFlyToDependencyMissing:
    """`nav.fly_to` result carried by `task_dependency_missing` (0x25)."""

    # This status carries no values.
    pass


class _NavFlyTo(TaskBinding):
    """fly to a waypoint

    Schema path `nav.fly_to`, uid 16.

    Returns one of:
      - `NavFlyToFinished` on `finished` (0x20)
      - `NavFlyToAborted` on `aborted` (0x21)
      - `NavFlyToDependencyMissing` on `task_dependency_missing` (0x25)
    ...or `UndeclaredResult` for any other completion status.
    """

    UID = TaskId.NAV_FLY_TO
    PATH = "nav.fly_to"
    PARAMS = ("double", "double", "float")
    SHAPES = build_shapes([
        (0x20, NavFlyToFinished, ("uint32",)),
        (0x21, NavFlyToAborted, ("double", "double", "float")),
        (0x25, NavFlyToDependencyMissing, ()),
    ])

    Finished = NavFlyToFinished
    Aborted = NavFlyToAborted
    DependencyMissing = NavFlyToDependencyMissing

    async def __call__(self, *, lat: float, lon: float, alt: float) -> NavFlyToFinished | NavFlyToAborted | NavFlyToDependencyMissing | UndeclaredResult:
        """Starts `nav.fly_to` and waits for its reply.

        Args:
            lat: `double`.
            lon: `double`.
            alt: `float`.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([lat, lon, alt])


class _NavHold(TaskBinding):
    """hold the current position

    Schema path `nav.hold`, uid 243.
    """

    UID = TaskId.NAV_HOLD
    PATH = "nav.hold"
    PARAMS = ()
    SHAPES = {}

    async def __call__(self) -> UndeclaredResult:
        """Starts `nav.hold` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _NavLand(TaskBinding):
    """descend and touch down

    Schema path `nav.land`, uid 41.
    """

    UID = TaskId.NAV_LAND
    PATH = "nav.land"
    PARAMS = ()
    SHAPES = {}

    async def __call__(self) -> UndeclaredResult:
        """Starts `nav.land` and waits for its reply.

        Raises:
            TaskRejected: the device refused to start the task.
        """
        return await self._invoke([])


class _Failsafe(InstantTaskBinding):
    """emergency stop - cut every rotor now

    Schema path `failsafe`, uid 255.

    A fire-and-forget command: it runs on the device the moment the
    request arrives and sends nothing back, so calling it returns
    immediately and there is no result to await. It cannot be paused,
    resumed, or completed - there is never a live instance to address.
    """

    UID = TaskId.FAILSAFE
    PATH = "failsafe"
    PARAMS = ()

    def __call__(self) -> None:
        """Runs `failsafe` on the device. Returns as soon as the request is sent.

        Nothing is returned and no exception is raised if the device
        rejects the command: an instant task sends no reply. Use a
        oneshot_task when the outcome matters.
        """
        self._dispatch([])


class _NavScope(Scope):
    """the navigation layer

    Schema scope `nav`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.fly_to = _NavFlyTo(client)
        self.hold = _NavHold(client)
        self.land = _NavLand(client)


class _SensorsGpsScope(Scope):
    """satellite positioning

    Schema scope `sensors.gps`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.fix = _SensorsGpsFix(client)


class _SensorsBaroScope(Scope):
    """barometric altimeter

    Schema scope `sensors.baro`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.read_altitude = _SensorsBaroReadAltitude(client)


class _SensorsImuScope(Scope):
    """inertial measurement unit

    Schema scope `sensors.imu`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.read = _SensorsImuRead(client)


class _SensorsScope(Scope):
    """the flight sensor suite

    Schema scope `sensors`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.imu = _SensorsImuScope(client)
        self.baro = _SensorsBaroScope(client)
        self.gps = _SensorsGpsScope(client)


class _RotorsRrScope(Scope):
    """the `rr` scope

    Schema scope `rotors.rr`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.set_thrust = _RotorsRrSetThrust(client)
        self.stop = _RotorsRrStop(client)


class _RotorsRlScope(Scope):
    """the `rl` scope

    Schema scope `rotors.rl`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.set_thrust = _RotorsRlSetThrust(client)
        self.stop = _RotorsRlStop(client)


class _RotorsFrScope(Scope):
    """the `fr` scope

    Schema scope `rotors.fr`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.set_thrust = _RotorsFrSetThrust(client)
        self.stop = _RotorsFrStop(client)


class _RotorsFlScope(Scope):
    """the `fl` scope

    Schema scope `rotors.fl`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.set_thrust = _RotorsFlSetThrust(client)
        self.stop = _RotorsFlStop(client)


class _RotorsScope(Scope):
    """the four-rotor array

    Schema scope `rotors`.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.fl = _RotorsFlScope(client)
        self.fr = _RotorsFrScope(client)
        self.rl = _RotorsRlScope(client)
        self.rr = _RotorsRrScope(client)


class Tasks(Scope):
    """The project's task tree, mirroring the schema's scopes.

    Construct it with a live `Client`; every task below is an
    awaitable call at the same path the schema declares.
    """

    UID_BYTES = UID_BYTES

    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.rotors = _RotorsScope(client)
        self.sensors = _SensorsScope(client)
        self.nav = _NavScope(client)
        self.failsafe = _Failsafe(client)
