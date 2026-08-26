from pathlib import Path

from siqoq.adapters import GeneratedSensor
from siqoq.conformance import assert_sensor_adapter_conformance
from siqoq.scenarios import JsonlFixtureSensor, run_fixture_scenario


FIXTURE = Path("examples/scenarios/person-detection.jsonl")


def test_generated_sensor_conforms() -> None:
    sample = assert_sensor_adapter_conformance(GeneratedSensor(count=1))
    assert sample.kind == "image"


def test_jsonl_fixture_sensor_conforms() -> None:
    sample = assert_sensor_adapter_conformance(JsonlFixtureSensor(FIXTURE))
    assert sample.source == "fixture.camera.front"
    assert sample.sequence == 0


def test_fixture_scenario_is_deterministic() -> None:
    summary = run_fixture_scenario(FIXTURE, name="person-detection")
    assert summary.name == "person-detection"
    assert summary.samples == 2
    assert summary.events == 2
    assert summary.actions == 2
    assert summary.rejected_actions == 0
    assert summary.architecture
