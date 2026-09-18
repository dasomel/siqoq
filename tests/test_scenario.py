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


def test_build_adapter_is_the_only_dispatch_point_on_adapter_type() -> None:
    """Guard the pipeline-level compatibility guarantee (issue #44).

    ``ScenarioConfig.build_adapter`` is the single place scenario.py branches
    on ``adapter``/source type; ``run_scenario`` itself must call
    ``adapter.read()`` through the shared ``SensorAdapter`` protocol with no
    additional type-specific branching. If this ever regresses (e.g. a new
    ``if config.adapter == ...`` sneaks into ``run_scenario``), Phase 2's
    "same downstream pipeline consumes simulated and real camera inputs"
    acceptance criterion would silently stop holding.
    """
    import inspect

    from siqoq import scenario as scenario_module

    run_scenario_source = inspect.getsource(scenario_module.run_scenario)

    assert "config.adapter" not in run_scenario_source
    assert "isinstance(adapter" not in run_scenario_source
    assert run_scenario_source.count("adapter.read(") == 1


def test_run_scenario_pipeline_shape_matches_across_generated_and_fixture_sources() -> None:
    """Same ScenarioConfig-driven pipeline, simulated vs. fixture/recorded source.

    Demonstrates the Phase 2 acceptance criterion end-to-end: running
    ``run_scenario`` against a simulated (``GeneratedSensorAdapter``) and a
    recorded (``FixtureSensorAdapter``) source through the identical
    ``run_scenario`` call yields ``ScenarioSummary`` objects with the same
    shape/fields, not just adapter-level conformance (already covered by the
    parametrized suite in tests/test_sensors.py).
    """
    generated_summary = run_scenario(ScenarioConfig(adapter="generated", steps=3))
    fixture_summary = run_scenario(
        ScenarioConfig(adapter="fixture", steps=3, source_path=str(FIXTURE_JSONL))
    )

    for summary in (generated_summary, fixture_summary):
        assert summary.event_count > 0
        assert set(summary.type_counts) == {"object.detected"}
        assert set(summary.action_counts)  # non-empty, exact action names are policy detail
        assert isinstance(summary.sequence_hash, str) and summary.sequence_hash
        assert summary.duration_seconds >= 0

    # Both runs went through the exact same ScenarioSummary field set
    # (ScenarioSummary uses slots=True, so fields() is used instead of vars()).
    import dataclasses

    generated_fields = {f.name for f in dataclasses.fields(generated_summary)}
    fixture_fields = {f.name for f in dataclasses.fields(fixture_summary)}
    assert generated_fields == fixture_fields
