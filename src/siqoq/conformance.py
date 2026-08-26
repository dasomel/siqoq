from __future__ import annotations

from .contracts import ActionRequest, Detection, SensorAdapter, SensorSample


def validate_sensor_sample(sample: SensorSample) -> None:
    if not sample.source.strip():
        raise ValueError("sensor source must not be empty")
    if not sample.kind.strip():
        raise ValueError("sensor kind must not be empty")
    if sample.sequence < 0:
        raise ValueError("sensor sequence must be >= 0")
    if not sample.timestamp.strip():
        raise ValueError("sensor timestamp must not be empty")


def validate_detection(detection: Detection) -> None:
    if not detection.label.strip():
        raise ValueError("detection label must not be empty")
    if not 0.0 <= detection.confidence <= 1.0:
        raise ValueError("detection confidence must be between 0 and 1")


def validate_action_request(request: ActionRequest) -> None:
    if not request.action.strip():
        raise ValueError("action must not be empty")
    if not request.target.strip():
        raise ValueError("action target must not be empty")


def assert_sensor_adapter_conformance(adapter: SensorAdapter) -> SensorSample:
    sample = adapter.read()
    if sample is None:
        raise AssertionError("sensor adapter must yield at least one sample for conformance")
    validate_sensor_sample(sample)
    return sample
