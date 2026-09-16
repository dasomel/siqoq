from pathlib import Path

from siqoq.events import SemanticEvent
from siqoq.policy import SafetyGate, decide
from siqoq.scenario import ScenarioConfig, run_scenario
from siqoq.sensors import FixtureSensorAdapter

FIXTURE_CONFIG = Path(__file__).parent / "fixtures" / "scenario_fixture.json"
FIXTURE_JSONL = Path(__file__).parent / "fixtures" / "recorded_detections.jsonl"


def test_from_json_loads_fixture_config() -> None:
    config = ScenarioConfig.from_json(FIXTURE_CONFIG)

    assert config.adapter == "fixture"
    assert config.steps == 3
    assert config.source_path == "tests/fixtures/recorded_detections.jsonl"


def test_run_scenario_is_deterministic(tmp_path: Path) -> None:
    config = ScenarioConfig(adapter="fixture", steps=3, source_path=str(FIXTURE_JSONL))

    first = run_scenario(config)
    second = run_scenario(config)

    assert first.event_count == 3
    assert first.type_counts == {"object.detected": 3}
    assert first.sequence_hash == second.sequence_hash


def test_run_scenario_writes_jsonl_output(tmp_path: Path) -> None:
    output_path = tmp_path / "events.jsonl"
    config = ScenarioConfig(
        adapter="fixture",
        steps=3,
        source_path=str(FIXTURE_JSONL),
        output_path=str(output_path),
    )

    summary = run_scenario(config)

    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == summary.event_count == 3


def test_run_scenario_with_generated_adapter() -> None:
    config = ScenarioConfig(adapter="generated", steps=2)

    summary = run_scenario(config)

    assert summary.event_count == 2
    assert summary.type_counts == {"object.detected": 2}


def test_fixture_regression_preserves_event_sequence_and_mock_safety(tmp_path: Path) -> None:
    output_path = tmp_path / "events.jsonl"
    summary = run_scenario(
        ScenarioConfig(
            adapter="fixture",
            steps=3,
            source_path=str(FIXTURE_JSONL),
            output_path=str(output_path),
        )
    )
    event = SemanticEvent.detected(source="sim.camera.front", object_name="person", confidence=0.9)

    assert summary.sequence_hash == (
        "25f893c180473bf3e429a034687ba64cafa19aca921162b4472c6012d37a2611"
    )
    assert decide(event, safety_gate=SafetyGate(allow_mock_actions=False)).action == "noop"


def test_missing_fixture_fails_without_fabricating_events(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jsonl"
    adapter = FixtureSensorAdapter(missing)

    import pytest

    with pytest.raises(FileNotFoundError):
        list(adapter.read(count=1))
