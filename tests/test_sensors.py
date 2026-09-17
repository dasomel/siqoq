from pathlib import Path

import pytest

from siqoq.events import REQUIRED_FIELDS
from siqoq.sensors import (
    CONTRACT_VERSION,
    FixtureSensorAdapter,
    GeneratedSensorAdapter,
    SensorAdapter,
)

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
def test_adapter_satisfies_sensor_contract_v0(adapter: SensorAdapter) -> None:
    """Sensor Contract v0 (docs/specs/sensor-contract.md): every fake and
    real/recorded adapter must yield events carrying all REQUIRED_FIELDS
    from the Semantic Event Contract, with a valid confidence range and a
    non-empty timestamp/source/object, regardless of adapter backend."""
    for event in adapter.read(count=1):
        for field_name in REQUIRED_FIELDS:
            assert hasattr(event, field_name), f"missing required field: {field_name}"
        assert 0 <= event.confidence <= 1
        assert isinstance(event.schema_version, int)


def test_sensor_contract_version_is_declared() -> None:
    assert isinstance(CONTRACT_VERSION, int)


@pytest.mark.parametrize("adapter", _adapters())
def test_adapter_is_deterministic_with_fixed_timestamp(adapter: SensorAdapter) -> None:
    first = [event.to_json() for event in adapter.read(count=2)]
    second = [event.to_json() for event in adapter.read(count=2)]
    assert first == second


def test_fixture_sensor_adapter_reports_line_number_for_malformed_rows(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text(
        '{"timestamp":"t","source":"s","object":"person","confidence":2}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match=r"line 1: confidence"):
        list(FixtureSensorAdapter(path).read(count=1))
