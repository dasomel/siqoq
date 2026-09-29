import base64
import json
import os
import sys
import types

import pytest

from siqoq.video_sensors import (
    MockWebcamFrameSensor,
    RecordedVideoFileSensor,
    UsbWebcamFrameSensor,
)


class _FakeFrame:
    """Stand-in for a cv2/numpy frame: exposes only .shape and .tobytes()."""

    def __init__(self, height: int, width: int, channels: int = 3, fill: int = 0):
        self.shape = (height, width, channels)
        self._data = bytes([fill % 256]) * (height * width * channels)

    def tobytes(self) -> bytes:
        return self._data


class _FakeVideoCapture:
    def __init__(self, device, *, opened=True, frames=None):
        self.device = device
        self._opened = opened
        self._frames = list(frames) if frames is not None else []
        self._read_index = 0
        self.released = False
        self.props: dict[int, float] = {}

    def isOpened(self) -> bool:
        return self._opened

    def set(self, prop_id, value) -> None:
        self.props[prop_id] = value

    def read(self):
        if self._read_index >= len(self._frames):
            return False, None
        frame = self._frames[self._read_index]
        self._read_index += 1
        return True, frame

    def release(self) -> None:
        self.released = True


def _make_fake_cv2(capture_factory):
    fake_cv2 = types.SimpleNamespace(
        CAP_PROP_FRAME_WIDTH=3,
        CAP_PROP_FRAME_HEIGHT=4,
        created_captures=[],
    )

    def video_capture(device):
        cap = capture_factory(device)
        fake_cv2.created_captures.append(cap)
        return cap

    fake_cv2.VideoCapture = video_capture
    return fake_cv2


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


def test_usb_webcam_sensor_reads_frames_with_correct_metadata(monkeypatch):
    frames = [_FakeFrame(2, 3), _FakeFrame(2, 3, fill=1)]
    fake_cv2 = _make_fake_cv2(lambda device: _FakeVideoCapture(device, frames=frames))
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)

    with UsbWebcamFrameSensor(device=0, source="webcam.usb") as sensor:
        first = sensor.read()
        second = sensor.read()
        third = sensor.read()

    assert first is not None
    assert first.metadata.source == "webcam.usb"
    assert first.metadata.index == 0
    assert first.metadata.width == 3
    assert first.metadata.height == 2
    assert first.metadata.format == "bgr24"
    assert first.payload == frames[0].tobytes()
    assert isinstance(first.payload, bytes)
    assert second is not None and second.metadata.index == 1
    assert second.payload == frames[1].tobytes()
    assert third is None


def test_usb_webcam_sensor_max_frames_exhaustion_returns_none(monkeypatch):
    frames = [_FakeFrame(2, 2), _FakeFrame(2, 2), _FakeFrame(2, 2)]
    fake_cv2 = _make_fake_cv2(lambda device: _FakeVideoCapture(device, frames=frames))
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)

    with UsbWebcamFrameSensor(device=0, max_frames=2) as sensor:
        results = [sensor.read(), sensor.read(), sensor.read()]

    assert results[0] is not None and results[1] is not None
    assert results[2] is None


def test_usb_webcam_sensor_ok_false_returns_none(monkeypatch):
    fake_cv2 = _make_fake_cv2(lambda device: _FakeVideoCapture(device, frames=[]))
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)

    with UsbWebcamFrameSensor(device=0) as sensor:
        result = sensor.read()

    assert result is None


def test_usb_webcam_sensor_device_fails_to_open_raises_runtime_error(monkeypatch):
    fake_cv2 = _make_fake_cv2(lambda device: _FakeVideoCapture(device, opened=False))
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)

    sensor = UsbWebcamFrameSensor(device=0)

    with pytest.raises(RuntimeError):
        sensor.open()


def test_usb_webcam_sensor_requires_open():
    sensor = UsbWebcamFrameSensor()

    with pytest.raises(RuntimeError):
        sensor.read()


def test_usb_webcam_sensor_missing_cv2_raises_import_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "cv2", None)
    sensor = UsbWebcamFrameSensor()

    with pytest.raises(ImportError):
        sensor.open()


def test_usb_webcam_sensor_close_releases_capture(monkeypatch):
    fake_cv2 = _make_fake_cv2(lambda device: _FakeVideoCapture(device, frames=[]))
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)

    sensor = UsbWebcamFrameSensor(device=0)
    sensor.open()
    cap = fake_cv2.created_captures[0]
    assert cap.released is False

    sensor.close()

    assert cap.released is True


def test_usb_webcam_sensor_reopen_releases_previous_capture(monkeypatch):
    fake_cv2 = _make_fake_cv2(lambda device: _FakeVideoCapture(device, frames=[]))
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)

    sensor = UsbWebcamFrameSensor(device=0)
    sensor.open()
    sensor.open()

    first, second = fake_cv2.created_captures
    assert first.released is True
    assert second.released is False


def test_usb_webcam_sensor_sets_requested_width_and_height(monkeypatch):
    fake_cv2 = _make_fake_cv2(lambda device: _FakeVideoCapture(device, frames=[]))
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)

    with UsbWebcamFrameSensor(device=0, width=640, height=480):
        cap = fake_cv2.created_captures[0]

    assert cap.props == {
        fake_cv2.CAP_PROP_FRAME_WIDTH: 640,
        fake_cv2.CAP_PROP_FRAME_HEIGHT: 480,
    }


@pytest.mark.skipif(
    os.environ.get("SIQOQ_WEBCAM_TEST") != "1",
    reason="requires SIQOQ_WEBCAM_TEST=1 and real webcam hardware",
)
def test_usb_webcam_sensor_reads_from_real_hardware():
    with UsbWebcamFrameSensor(device=0, max_frames=1) as sensor:
        frame = sensor.read()

    assert frame is not None
    assert frame.metadata.width > 0
    assert frame.metadata.height > 0
