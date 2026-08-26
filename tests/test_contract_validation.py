import pytest

from siqoq.contracts import ActionRequest, Detection, SensorSample


def test_sensor_sample_rejects_negative_sequence() -> None:
    with pytest.raises(ValueError, match="sequence"):
        SensorSample(
            source="fixture.camera.front",
            kind="image",
            timestamp="2026-01-01T00:00:00+00:00",
            sequence=-1,
        )


def test_detection_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError, match="confidence"):
        Detection(label="person", confidence=1.1)


def test_action_request_requires_action_and_target() -> None:
    with pytest.raises(ValueError, match="action"):
        ActionRequest(action="", target="demo")
    with pytest.raises(ValueError, match="target"):
        ActionRequest(action="indicator.on", target="")
