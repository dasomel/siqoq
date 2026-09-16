from siqoq.events import SemanticEvent
from siqoq.policy import decide


def test_decide_is_deterministic_and_mock_only() -> None:
    event = SemanticEvent.detected(source="sim.camera.front", object_name="person", confidence=0.9)

    first = decide(event)
    second = decide(event)

    assert first == second
    assert first.mock is True
    assert first.action == "log_detection"


def test_decide_defaults_unknown_event_types_to_noop() -> None:
    event = SemanticEvent(
        type="object.lost",
        source="sim.camera.front",
        object="person",
        confidence=0.5,
        timestamp="2026-01-01T00:00:00+00:00",
    )

    assert decide(event).action == "noop"
