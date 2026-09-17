from siqoq.events import PROVENANCE_RECORDED, PROVENANCE_SIMULATED, SemanticEvent


def test_detected_event_serializes() -> None:
    event = SemanticEvent.detected(
        source="sim.camera.front",
        object_name="person",
        confidence=0.94,
    )

    payload = event.to_json()

    assert '"type":"object.detected"' in payload
    assert '"source":"sim.camera.front"' in payload
    assert '"object":"person"' in payload
    assert '"confidence":0.94' in payload
    assert '"schema_version":1' in payload


def test_detected_event_omits_empty_optional_fields() -> None:
    event = SemanticEvent.detected(
        source="sim.camera.front",
        object_name="person",
        confidence=0.94,
    )

    payload = event.to_json()

    assert "correlation_id" not in payload
    assert "metadata" not in payload


def test_detected_event_includes_optional_fields_when_set() -> None:
    event = SemanticEvent.detected(
        source="sim.camera.front",
        object_name="person",
        confidence=0.94,
        correlation_id="corr-1",
        metadata={"frame_id": 42},
    )

    payload = event.to_json()

    assert '"correlation_id":"corr-1"' in payload
    assert '"frame_id":42' in payload


def test_provenance_metadata_convention_is_additive() -> None:
    """Semantic Event Contract v0 provenance convention (docs/specs/
    semantic-event-contract.md): metadata["provenance"] is additive on top
    of the existing free-form metadata dict, not a new required field."""
    simulated = SemanticEvent.detected(
        source="sim.camera.front",
        object_name="person",
        confidence=0.94,
        metadata={"provenance": PROVENANCE_SIMULATED},
    )
    recorded = SemanticEvent.detected(
        source="file.video.recorded",
        object_name="person",
        confidence=0.94,
        metadata={"provenance": PROVENANCE_RECORDED},
    )

    assert '"provenance":"simulated"' in simulated.to_json()
    assert '"provenance":"recorded"' in recorded.to_json()

    # Absence of provenance must stay valid: older/non-conforming producers
    # are still schema-conformant per the "additive-only" compatibility rule.
    no_provenance = SemanticEvent.detected(
        source="sim.camera.front", object_name="person", confidence=0.94
    )
    assert "provenance" not in no_provenance.to_json()
