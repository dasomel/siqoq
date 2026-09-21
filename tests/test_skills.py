from __future__ import annotations

import json
import subprocess
import sys

from siqoq.events import SemanticEvent
from siqoq.skills import classify, list_catalog


def test_classify_matches_object_detection_for_object_detected() -> None:
    event = SemanticEvent.detected(
        source="sim.camera.front", object_name="person", confidence=0.9
    )
    assert classify(event) == ["object-detection"]


def test_classify_returns_empty_for_unknown_type() -> None:
    event = SemanticEvent(
        type="unknown.event",
        source="test",
        object="thing",
        confidence=0.5,
        timestamp="2026-09-21T00:00:00+00:00",
    )
    assert classify(event) == []


def test_list_catalog_returns_at_least_one_entry() -> None:
    catalog = list_catalog()
    assert len(catalog) >= 1
    assert any(skill.name == "object-detection" for skill in catalog)


def test_cli_skills_list_produces_valid_json() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "siqoq.cli", "skills", "list"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert isinstance(payload, list)
    assert any(entry["name"] == "object-detection" for entry in payload)


def test_cli_skills_classify_produces_valid_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "siqoq.cli",
            "skills",
            "classify",
            "--event-type",
            "object.detected",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload == ["object-detection"]
