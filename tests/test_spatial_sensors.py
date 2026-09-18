from pathlib import Path

import pytest

from siqoq.spatial_sensors import (
    FixtureDepthSensor,
    FixtureImuSensor,
    FixtureLidarSensor,
    MockDepthSensor,
    MockImuSensor,
    MockLidarSensor,
    RealLidarSensor,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_mock_lidar_sensor_requires_open():
    sensor = MockLidarSensor()

    with pytest.raises(RuntimeError):
        sensor.read()


def test_mock_lidar_sensor_deterministic_replay():
    def run():
        with MockLidarSensor(num_ranges=3, scan_count=2) as sensor:
            return [sensor.read(), sensor.read(), sensor.read()]

    first_run = run()
    second_run = run()

    assert first_run == second_run
    assert first_run[0] is not None and first_run[0].index == 0
    assert first_run[1] is not None and first_run[1].index == 1
    assert first_run[2] is None


def test_mock_depth_sensor_deterministic_replay():
    def run():
        with MockDepthSensor(width=2, height=2, frame_count=2) as sensor:
            return [sensor.read(), sensor.read(), sensor.read()]

    first_run = run()
    second_run = run()

    assert first_run == second_run
    assert first_run[0] is not None and len(first_run[0].depths) == 4
    assert first_run[2] is None


def test_mock_imu_sensor_deterministic_replay():
    def run():
        with MockImuSensor(sample_count=2) as sensor:
            return [sensor.read(), sensor.read(), sensor.read()]

    first_run = run()
    second_run = run()

    assert first_run == second_run
    assert first_run[0] is not None
    assert first_run[0].linear_acceleration == (0.0, 0.0, 9.8)
    assert first_run[2] is None


def test_mock_depth_sensor_requires_open():
    sensor = MockDepthSensor()

    with pytest.raises(RuntimeError):
        sensor.read()


def test_mock_imu_sensor_requires_open():
    sensor = MockImuSensor()

    with pytest.raises(RuntimeError):
        sensor.read()


def test_fixture_lidar_sensor_round_trip():
    with FixtureLidarSensor(path=FIXTURES_DIR / "lidar_scans.jsonl") as sensor:
        first = sensor.read()
        second = sensor.read()
        third = sensor.read()

    assert first is not None and first.timestamp == "t0"
    assert first.ranges == [1.0, 1.5, 2.0]
    assert second is not None and second.index == 1
    assert third is None


def test_fixture_lidar_sensor_requires_open(tmp_path):
    path = tmp_path / "empty.jsonl"
    path.write_text("")
    sensor = FixtureLidarSensor(path=path)

    with pytest.raises(RuntimeError):
        sensor.read()


def test_fixture_depth_sensor_round_trip():
    with FixtureDepthSensor(path=FIXTURES_DIR / "depth_frames.jsonl") as sensor:
        first = sensor.read()
        second = sensor.read()
        third = sensor.read()

    assert first is not None and first.width == 2 and first.height == 2
    assert first.depths == [0.5, 0.6, 0.7, 0.8]
    assert second is not None and second.index == 1
    assert third is None


def test_fixture_depth_sensor_requires_open(tmp_path):
    path = tmp_path / "empty.jsonl"
    path.write_text("")
    sensor = FixtureDepthSensor(path=path)

    with pytest.raises(RuntimeError):
        sensor.read()


def test_fixture_imu_sensor_round_trip():
    with FixtureImuSensor(path=FIXTURES_DIR / "imu_samples.jsonl") as sensor:
        first = sensor.read()
        second = sensor.read()
        third = sensor.read()

    assert first is not None and first.timestamp == "t0"
    assert first.linear_acceleration == (0.0, 0.0, 9.8)
    assert second is not None and second.angular_velocity == (0.0, 0.1, 0.0)
    assert third is None


def test_fixture_imu_sensor_requires_open(tmp_path):
    path = tmp_path / "empty.jsonl"
    path.write_text("")
    sensor = FixtureImuSensor(path=path)

    with pytest.raises(RuntimeError):
        sensor.read()


def test_real_lidar_sensor_is_a_documented_stub():
    sensor = RealLidarSensor()

    with pytest.raises(NotImplementedError):
        sensor.open()
