from pathlib import Path

import pytest

from siqoq.scenario import CatalogResult, load_catalog, run_catalog_entry

CATALOG_PATH = Path(__file__).parent.parent / "examples" / "scenarios" / "catalog.json"


def _run_all() -> list[CatalogResult]:
    entries = load_catalog(CATALOG_PATH)
    return [run_catalog_entry(entry, base_dir=CATALOG_PATH.parent) for entry in entries]


def test_load_catalog_has_at_least_three_scenarios() -> None:
    entries = load_catalog(CATALOG_PATH)
    assert len(entries) >= 3


@pytest.mark.parametrize(
    "entry_id",
    [
        "recorded-video-detection",
        "simulated-camera-detection",
        "sensor-disconnect",
        "inference-fallback-on-bad-input",
        "action-rejected-by-safety-gate",
        "scene-single-object",
        "scene-multi-step-sequence",
    ],
)
def test_catalog_entry_passes(entry_id: str) -> None:
    entries = {entry.id: entry for entry in load_catalog(CATALOG_PATH)}
    entry = entries[entry_id]

    result = run_catalog_entry(entry, base_dir=CATALOG_PATH.parent)

    assert result.passed, result.detail


def test_full_catalog_run_reports_pass_fail_per_scenario() -> None:
    results = _run_all()

    assert len(results) == 7
    assert all(result.passed for result in results), [
        (r.entry_id, r.detail) for r in results if not r.passed
    ]


def test_scenario_summary_carries_action_counts_and_duration() -> None:
    entries = {entry.id: entry for entry in load_catalog(CATALOG_PATH)}
    result = run_catalog_entry(
        entries["action-rejected-by-safety-gate"], base_dir=CATALOG_PATH.parent
    )

    assert result.summary is not None
    assert result.summary.action_counts == {"noop": 3}
    assert result.summary.duration_seconds >= 0.0


@pytest.mark.parametrize("scene_id", ["scene-single-object", "scene-multi-step-sequence"])
def test_scene_sequence_hash_is_deterministic_across_runs(scene_id: str) -> None:
    entries = {entry.id: entry for entry in load_catalog(CATALOG_PATH)}
    entry = entries[scene_id]
    assert entry.kind == "scene"
    assert entry.version is not None

    first = run_catalog_entry(entry, base_dir=CATALOG_PATH.parent)
    second = run_catalog_entry(entry, base_dir=CATALOG_PATH.parent)

    assert first.passed and second.passed
    assert first.summary is not None and second.summary is not None
    assert first.summary.sequence_hash == second.summary.sequence_hash
