from __future__ import annotations

import json

from siqoq.actuation import ActionResult
from siqoq.events import SemanticEvent
from siqoq.trace import DecisionTrace, build_trace


def _event(**overrides) -> SemanticEvent:
    return SemanticEvent.detected(
        source="sim.camera.front",
        object_name="person",
        confidence=0.9,
        correlation_id=overrides.pop("correlation_id", "corr-1"),
        metadata=overrides.pop("metadata", None),
    )


def test_build_trace_correlates_event_and_action() -> None:
    event = _event()
    result = ActionResult(
        action="log_detection",
        event_type=event.type,
        outcome="executed",
        correlation_id=event.correlation_id,
        timestamp="2026-01-01T00:00:00+00:00",
    )

    trace = build_trace(event, result)

    assert trace.correlation_id == "corr-1"
    assert trace.event_type == event.type
    assert trace.event_source == event.source
    assert trace.event_confidence == event.confidence
    assert trace.action == "log_detection"
    assert trace.action_outcome == "executed"
    assert trace.action_timestamp == "2026-01-01T00:00:00+00:00"


def test_build_trace_event_only_has_no_action_fields() -> None:
    event = _event()

    trace = build_trace(event)

    assert trace.action is None
    assert trace.action_outcome is None
    assert trace.action_timestamp is None
    payload = json.loads(trace.to_json())
    assert "action" not in payload
    assert "action_outcome" not in payload
    assert "action_timestamp" not in payload


def test_build_trace_redacts_metadata_by_default() -> None:
    event = _event(metadata={"frame_bytes": "sensitive-fake-data"})

    trace = build_trace(event)

    assert trace.metadata is None
    payload = json.loads(trace.to_json())
    assert "metadata" not in payload
    assert "sensitive-fake-data" not in trace.to_json()


def test_build_trace_includes_metadata_when_opted_in() -> None:
    event = _event(metadata={"frame_bytes": "sensitive-fake-data"})

    trace = build_trace(event, include_metadata=True)

    assert trace.metadata == {"frame_bytes": "sensitive-fake-data"}
    payload = json.loads(trace.to_json())
    assert payload["metadata"] == {"frame_bytes": "sensitive-fake-data"}


def test_decision_trace_to_json_omits_empty_optionals() -> None:
    trace = DecisionTrace(
        correlation_id=None,
        event_type="object.detected",
        event_source="sim.camera.front",
        event_confidence=0.5,
        event_timestamp="2026-01-01T00:00:00+00:00",
        action=None,
        action_outcome=None,
        action_timestamp=None,
        metadata=None,
    )

    payload = json.loads(trace.to_json())

    assert payload == {
        "event_type": "object.detected",
        "event_source": "sim.camera.front",
        "event_confidence": 0.5,
        "event_timestamp": "2026-01-01T00:00:00+00:00",
    }
