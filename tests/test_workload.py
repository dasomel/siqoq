from __future__ import annotations

import json
import subprocess
import sys

from siqoq.capabilities import discover
from siqoq.workload import WorkloadSpec


def test_satisfiable_spec_has_no_reasons(tmp_path) -> None:
    spec = WorkloadSpec(
        name="ok",
        scenario_config_path="examples/scenarios/fixture_detection.json",
        required_capabilities={"vision_extra_available": False},
    )
    assert spec.validate_against(discover()) == []


def test_unsatisfiable_spec_names_missing_capability() -> None:
    spec = WorkloadSpec(
        name="needs-vision",
        scenario_config_path="examples/scenarios/fixture_detection.json",
        required_capabilities={"vision_extra_available": True},
    )
    reasons = spec.validate_against(discover())
    assert len(reasons) == 1
    assert "vision_extra_available" in reasons[0]
    assert "False" in reasons[0]


def test_unknown_required_capability_key_is_reported() -> None:
    spec = WorkloadSpec(
        name="bogus",
        scenario_config_path="examples/scenarios/fixture_detection.json",
        required_capabilities={"nonexistent_field": True},
    )
    reasons = spec.validate_against(discover())
    assert any("nonexistent_field" in r for r in reasons)


def test_from_json_round_trips(tmp_path) -> None:
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(
        json.dumps(
            {
                "name": "roundtrip",
                "scenario_config_path": "examples/scenarios/fixture_detection.json",
                "required_capabilities": {"vision_extra_available": False},
                "resource_hints": {"min_memory_mb": 256},
            }
        ),
        encoding="utf-8",
    )
    spec = WorkloadSpec.from_json(spec_path)
    assert spec.name == "roundtrip"
    assert spec.resource_hints == {"min_memory_mb": 256}


def test_cli_workload_validate_pass_case_prints_valid_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "siqoq.cli",
            "workload",
            "validate",
            "--spec",
            "examples/workloads/fixture_detection_workload.json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["satisfiable"] is True
    assert payload["reasons"] == []


def test_cli_workload_validate_fail_case_prints_valid_json(tmp_path) -> None:
    spec_path = tmp_path / "unsatisfiable.json"
    spec_path.write_text(
        json.dumps(
            {
                "name": "needs-vision",
                "scenario_config_path": "examples/scenarios/fixture_detection.json",
                "required_capabilities": {"vision_extra_available": True},
            }
        ),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "siqoq.cli", "workload", "validate", "--spec", str(spec_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["satisfiable"] is False
    assert len(payload["reasons"]) == 1
