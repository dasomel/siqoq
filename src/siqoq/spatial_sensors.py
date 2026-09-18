"""Spatial sensor adapters: LiDAR, depth camera, and IMU (mock/fixture-only).

Extends the frame-level pattern in ``video_sensors.py`` (Sensor Contract v0,
see docs/specs/sensor-contract.md) to non-visual spatial sensors. Real
LiDAR/depth-camera/IMU hardware access requires vendor SDKs or drivers (e.g.
pyrealsense2, a ROS 2 LiDAR driver, a serial IMU protocol) that are not
approved dependencies for this project. To stay hardware- and
dependency-free, this module ships only:

- Deterministic mock generators (``MockLidarSensor``, ``MockDepthSensor``,
  ``MockImuSensor``) producing fixed/pattern-based synthetic data, no
  randomness.
- Deterministic JSONL fixture replay backends (``FixtureLidarSensor``,
  ``FixtureDepthSensor``, ``FixtureImuSensor``), mirroring
  ``RecordedVideoFileSensor``'s read-before-open-raises / replay pattern.

Design decision: one generalized protocol, not three. LiDAR, depth, and IMU
share the exact same open/read/close lifecycle contract as ``FrameSensor``
(explicit open before read, ``read()`` returns ``None`` on exhaustion instead
of raising, idempotent-safe close) and differ only in the payload type
``read()`` returns. Python's structural `Protocol` typing lets a single
generic ``SpatialSensor[T]`` express "same lifecycle, different payload"
without three near-identical protocol bodies to keep in sync. If a future
sensor type needs a genuinely different lifecycle (e.g. batched reads), split
it out then rather than pre-emptively forking now.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

#: Sensor Contract v0 version for the spatial-sensor layer. Bump on breaking
#: changes to the open/read/close lifecycle or the required fields of
#: LidarScan/DepthFrame/ImuSample (see docs/specs/sensor-contract.md).
CONTRACT_VERSION = 0


@dataclass(slots=True, frozen=True)
class LidarScan:
    """Normalized single 2D LiDAR scan (analogous to Frame for video)."""

    source: str
    index: int
    timestamp: str
    angle_min: float
    angle_max: float
    ranges: list[float]


@dataclass(slots=True, frozen=True)
class DepthFrame:
    """Normalized depth-camera frame: flat row-major depth values."""

    source: str
    index: int
    timestamp: str
    width: int
    height: int
    depths: list[float]


@dataclass(slots=True, frozen=True)
class ImuSample:
    """Normalized single IMU sample."""

    source: str
    index: int
    timestamp: str
    linear_acceleration: tuple[float, float, float]
    angular_velocity: tuple[float, float, float]


class SpatialSensor[T](Protocol):
    """Common lifecycle for LiDAR/depth/IMU sources, mirroring FrameSensor.

    Callers must ``open()`` before ``read()`` and ``close()`` when done.
    ``read()`` returns ``None`` once the source is exhausted instead of
    raising.
    """

    def open(self) -> None: ...

    def read(self) -> T | None: ...

    def close(self) -> None: ...

    def __enter__(self) -> SpatialSensor[T]:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


@dataclass(slots=True)
class MockLidarSensor:
    """Hardware-free deterministic LiDAR scan generator."""

    source: str = "lidar.mock.front"
    num_ranges: int = 4
    scan_count: int = 3
    angle_min: float = -1.57
    angle_max: float = 1.57
    _opened: bool = False
    _index: int = 0

    def open(self) -> None:
        self._opened = True
        self._index = 0

    def read(self) -> LidarScan | None:
        if not self._opened:
            raise RuntimeError("MockLidarSensor.read() called before open()")
        if self._index >= self.scan_count:
            return None
        ranges = [float(self._index + i) for i in range(self.num_ranges)]
        scan = LidarScan(
            source=self.source,
            index=self._index,
            timestamp=f"mock-lidar-{self._index}",
            angle_min=self.angle_min,
            angle_max=self.angle_max,
            ranges=ranges,
        )
        self._index += 1
        return scan

    def close(self) -> None:
        self._opened = False
        self._index = 0

    def __enter__(self) -> MockLidarSensor:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


@dataclass(slots=True)
class MockDepthSensor:
    """Hardware-free deterministic depth-camera frame generator."""

    source: str = "depth.mock.front"
    width: int = 2
    height: int = 2
    frame_count: int = 3
    _opened: bool = False
    _index: int = 0

    def open(self) -> None:
        self._opened = True
        self._index = 0

    def read(self) -> DepthFrame | None:
        if not self._opened:
            raise RuntimeError("MockDepthSensor.read() called before open()")
        if self._index >= self.frame_count:
            return None
        depths = [float(self._index) for _ in range(self.width * self.height)]
        frame = DepthFrame(
            source=self.source,
            index=self._index,
            timestamp=f"mock-depth-{self._index}",
            width=self.width,
            height=self.height,
            depths=depths,
        )
        self._index += 1
        return frame

    def close(self) -> None:
        self._opened = False
        self._index = 0

    def __enter__(self) -> MockDepthSensor:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


@dataclass(slots=True)
class MockImuSensor:
    """Hardware-free deterministic IMU sample generator."""

    source: str = "imu.mock.body"
    sample_count: int = 3
    _opened: bool = False
    _index: int = 0

    def open(self) -> None:
        self._opened = True
        self._index = 0

    def read(self) -> ImuSample | None:
        if not self._opened:
            raise RuntimeError("MockImuSensor.read() called before open()")
        if self._index >= self.sample_count:
            return None
        value = float(self._index)
        sample = ImuSample(
            source=self.source,
            index=self._index,
            timestamp=f"mock-imu-{self._index}",
            linear_acceleration=(value, 0.0, 9.8),
            angular_velocity=(0.0, value, 0.0),
        )
        self._index += 1
        return sample

    def close(self) -> None:
        self._opened = False
        self._index = 0

    def __enter__(self) -> MockImuSensor:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


@dataclass(slots=True)
class FixtureLidarSensor:
    """Reads LiDAR scans from a deterministic JSONL fixture file.

    Each line: ``{"timestamp": ..., "angle_min": ..., "angle_max": ...,
    "ranges": [...]}``.
    """

    path: Path
    source: str = "lidar.fixture.recorded"
    _lines: list[str] | None = None
    _index: int = 0

    def open(self) -> None:
        with self.path.open(encoding="utf-8") as handle:
            self._lines = [line for line in handle if line.strip()]
        self._index = 0

    def read(self) -> LidarScan | None:
        if self._lines is None:
            raise RuntimeError("FixtureLidarSensor.read() called before open()")
        if self._index >= len(self._lines):
            return None
        record = json.loads(self._lines[self._index])
        scan = LidarScan(
            source=self.source,
            index=self._index,
            timestamp=record["timestamp"],
            angle_min=record["angle_min"],
            angle_max=record["angle_max"],
            ranges=list(record["ranges"]),
        )
        self._index += 1
        return scan

    def close(self) -> None:
        self._lines = None
        self._index = 0

    def __enter__(self) -> FixtureLidarSensor:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


@dataclass(slots=True)
class FixtureDepthSensor:
    """Reads depth frames from a deterministic JSONL fixture file.

    Each line: ``{"timestamp": ..., "width": ..., "height": ...,
    "depths": [...]}``.
    """

    path: Path
    source: str = "depth.fixture.recorded"
    _lines: list[str] | None = None
    _index: int = 0

    def open(self) -> None:
        with self.path.open(encoding="utf-8") as handle:
            self._lines = [line for line in handle if line.strip()]
        self._index = 0

    def read(self) -> DepthFrame | None:
        if self._lines is None:
            raise RuntimeError("FixtureDepthSensor.read() called before open()")
        if self._index >= len(self._lines):
            return None
        record = json.loads(self._lines[self._index])
        frame = DepthFrame(
            source=self.source,
            index=self._index,
            timestamp=record["timestamp"],
            width=record["width"],
            height=record["height"],
            depths=list(record["depths"]),
        )
        self._index += 1
        return frame

    def close(self) -> None:
        self._lines = None
        self._index = 0

    def __enter__(self) -> FixtureDepthSensor:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


@dataclass(slots=True)
class FixtureImuSensor:
    """Reads IMU samples from a deterministic JSONL fixture file.

    Each line: ``{"timestamp": ..., "linear_acceleration": [x, y, z],
    "angular_velocity": [x, y, z]}``.
    """

    path: Path
    source: str = "imu.fixture.recorded"
    _lines: list[str] | None = None
    _index: int = 0

    def open(self) -> None:
        with self.path.open(encoding="utf-8") as handle:
            self._lines = [line for line in handle if line.strip()]
        self._index = 0

    def read(self) -> ImuSample | None:
        if self._lines is None:
            raise RuntimeError("FixtureImuSensor.read() called before open()")
        if self._index >= len(self._lines):
            return None
        record = json.loads(self._lines[self._index])
        accel = record["linear_acceleration"]
        gyro = record["angular_velocity"]
        sample = ImuSample(
            source=self.source,
            index=self._index,
            timestamp=record["timestamp"],
            linear_acceleration=(accel[0], accel[1], accel[2]),
            angular_velocity=(gyro[0], gyro[1], gyro[2]),
        )
        self._index += 1
        return sample

    def close(self) -> None:
        self._lines = None
        self._index = 0

    def __enter__(self) -> FixtureImuSensor:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


@dataclass(slots=True)
class RealLidarSensor:
    """Real LiDAR hardware backend contract (not implemented).

    A real implementation needs a vendor/ROS 2 LiDAR driver dependency not
    yet approved for this project (see pyproject.toml). Use
    ``MockLidarSensor``/``FixtureLidarSensor`` for development and CI;
    implement this backend in a follow-up once a dependency is approved.
    """

    device: str = "/dev/lidar0"

    def open(self) -> None:
        raise NotImplementedError(
            "Real LiDAR capture is not implemented; no approved LiDAR "
            "driver dependency yet. Use MockLidarSensor/FixtureLidarSensor "
            "for development, or implement this backend in a follow-up "
            "(see module docstring)."
        )

    def read(self) -> LidarScan | None:
        raise NotImplementedError("RealLidarSensor.open() must succeed first")

    def close(self) -> None:
        return None

    def __enter__(self) -> RealLidarSensor:
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
