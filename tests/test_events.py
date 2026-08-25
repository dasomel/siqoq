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
