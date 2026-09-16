import base64
import json

import pytest

from siqoq.video_sensors import (
    MockWebcamFrameSensor,
    RecordedVideoFileSensor,
    UsbWebcamFrameSensor,
)


def _write_fixture(tmp_path, frames):
    path = tmp_path / "frames.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for frame in frames:
            handle.write(json.dumps(frame) + "\n")
    return path


def test_recorded_video_file_sensor_reads_frames_then_none(tmp_path):
    frames = [
        {
            "timestamp": "t0",
            "width": 2,
            "height": 2,
            "format": "raw",
            "payload_b64": base64.b64encode(b"abcd").decode("ascii"),
        },
        {
            "timestamp": "t1",
            "width": 2,
            "height": 2,
            "format": "raw",
            "payload_b64": base64.b64encode(b"efgh").decode("ascii"),
        },
    ]
    path = _write_fixture(tmp_path, frames)

    with RecordedVideoFileSensor(path=path) as sensor:
        first = sensor.read()
        second = sensor.read()
        third = sensor.read()

    assert first is not None and first.metadata.index == 0
    assert first.metadata.timestamp == "t0"
    assert first.payload == b"abcd"
    assert second is not None and second.metadata.index == 1
    assert second.payload == b"efgh"
    assert third is None


def test_recorded_video_file_sensor_requires_open(tmp_path):
    path = _write_fixture(tmp_path, [])
    sensor = RecordedVideoFileSensor(path=path)

    with pytest.raises(RuntimeError):
        sensor.read()


def test_mock_webcam_sensor_yields_deterministic_frames():
    with MockWebcamFrameSensor(frame_count=2, width=2, height=2) as sensor:
        first = sensor.read()
        second = sensor.read()
        third = sensor.read()

    assert first is not None and first.metadata.source == "webcam.mock.front"
    assert first.metadata.width == 2 and first.metadata.height == 2
    assert second is not None and second.metadata.index == 1
    assert third is None


def test_mock_webcam_sensor_requires_open():
    sensor = MockWebcamFrameSensor()

    with pytest.raises(RuntimeError):
        sensor.read()


def test_usb_webcam_sensor_is_a_documented_stub():
    sensor = UsbWebcamFrameSensor()

    with pytest.raises(NotImplementedError):
        sensor.open()
