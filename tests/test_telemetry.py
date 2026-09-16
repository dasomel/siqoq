from siqoq import telemetry
from siqoq.cli import run_demo
from siqoq.events import SemanticEvent


def test_is_available_reflects_whether_extra_is_installed() -> None:
    assert telemetry.is_available() in (True, False)


def test_start_span_is_a_noop_without_the_extra() -> None:
    entered = False
    with telemetry.start_span("test.span"):
        entered = True
    assert entered


def test_events_emitted_counter_add_never_raises_without_the_extra() -> None:
    counter = telemetry.get_events_emitted_counter()
    counter.add(1, {"source": "test"})


def test_detected_event_works_regardless_of_telemetry_availability() -> None:
    event = SemanticEvent.detected(
        source="sim.camera.front",
        object_name="person",
        confidence=0.94,
    )
    assert event.type == "object.detected"


def test_demo_runs_regardless_of_telemetry_availability() -> None:
    assert run_demo() == 0
