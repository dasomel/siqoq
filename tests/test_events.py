from siqoq.events import SemanticEvent


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
