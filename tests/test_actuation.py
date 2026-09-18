from __future__ import annotations

import json
import re
from pathlib import Path

from siqoq.actuation import ActionResult, MockActuatorAdapter, decide_and_execute
from siqoq.events import SemanticEvent
from siqoq.policy import MockAction, SafetyGate


def test_policy_module_never_imports_actuation() -> None:
    """policy.py must not import actuation.py: reasoning never directly
    controls "hardware" (docs/specs/action-contract.md safety review)."""
    policy_src = Path(__file__).resolve().parent.parent / "src" / "siqoq" / "policy.py"
    src = policy_src.read_text()
    assert re.search(r"^\s*(import|from)\s+.*actuation", src, re.MULTILINE) is None
    assert "actuation" not in src


def test_mock_adapter_executes_only_mock_safe_non_default_actions() -> None:
    adapter = MockActuatorAdapter()

    action = MockAction(action="log_detection", event_type="object.detected", mock=True)
    result = adapter.execute(action)

    assert result.outcome == "executed"
    assert result.action == "log_detection"
    assert result.event_type == "object.detected"


def test_mock_adapter_returns_noop_for_default_action() -> None:
    adapter = MockActuatorAdapter()

    action = MockAction(action="noop", event_type="object.lost", mock=True)
    result = adapter.execute(action)

    assert result.outcome == "noop"


def test_mock_adapter_rejects_non_mock_action() -> None:
    adapter = MockActuatorAdapter()

    action = MockAction(action="log_detection", event_type="object.detected", mock=False)
    result = adapter.execute(action)

    assert result.outcome == "rejected"


def test_action_result_round_trips_through_to_json() -> None:
    result = ActionResult(
        action="log_detection",
        event_type="object.detected",
        outcome="executed",
        correlation_id="corr-1",
        timestamp="2026-01-01T00:00:00+00:00",
    )

    payload = json.loads(result.to_json())

    assert payload == {
        "action": "log_detection",
        "event_type": "object.detected",
        "outcome": "executed",
        "correlation_id": "corr-1",
        "timestamp": "2026-01-01T00:00:00+00:00",
    }


def test_action_result_to_json_omits_none_correlation_id() -> None:
    result = ActionResult(
        action="noop",
        event_type="object.lost",
        outcome="noop",
        correlation_id=None,
        timestamp="2026-01-01T00:00:00+00:00",
    )

    payload = json.loads(result.to_json())

    assert "correlation_id" not in payload


def test_safety_gate_denial_never_results_in_executed() -> None:
    event = SemanticEvent.detected(source="sim.camera.front", object_name="person", confidence=0.9)
    adapter = MockActuatorAdapter()

    result = decide_and_execute(
        event,
        adapter=adapter,
        safety_gate=SafetyGate(allow_mock_actions=False),
    )

    assert result.outcome in ("rejected", "noop")
    assert result.outcome != "executed"


def test_decide_and_execute_propagates_correlation_id() -> None:
    event = SemanticEvent.detected(
        source="sim.camera.front",
        object_name="person",
        confidence=0.9,
        correlation_id="trace-42",
    )
    adapter = MockActuatorAdapter()

    result = decide_and_execute(event, adapter=adapter)

    assert result.outcome == "executed"
    assert result.correlation_id == "trace-42"
