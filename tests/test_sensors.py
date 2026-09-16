from pathlib import Path

import pytest

from siqoq.sensors import FixtureSensorAdapter, GeneratedSensorAdapter, SensorAdapter

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "recorded_detections.jsonl"


def _adapters() -> list[SensorAdapter]:
    return [
        GeneratedSensorAdapter(timestamp="2026-01-01T00:00:00+00:00"),
        FixtureSensorAdapter(path=FIXTURE_PATH),
    ]


@pytest.mark.parametrize("adapter", _adapters())
def test_adapter_yields_requested_count(adapter: SensorAdapter) -> None:
    events = list(adapter.read(count=2))
    assert len(events) == 2


@pytest.mark.parametrize("adapter", _adapters())
def test_adapter_events_share_semantic_event_shape(adapter: SensorAdapter) -> None:
    for event in adapter.read(count=1):
        assert event.type == "object.detected"
        assert isinstance(event.source, str) and event.source
        assert isinstance(event.object, str) and event.object
        assert isinstance(event.confidence, float)
        assert isinstance(event.timestamp, str) and event.timestamp


@pytest.mark.parametrize("adapter", _adapters())
def test_adapter_is_deterministic_with_fixed_timestamp(adapter: SensorAdapter) -> None:
    first = [event.to_json() for event in adapter.read(count=2)]
    second = [event.to_json() for event in adapter.read(count=2)]
    assert first == second
