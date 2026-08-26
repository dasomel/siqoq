import json

from siqoq.adapters import JsonlTransport
from siqoq.events import SemanticEvent


def test_jsonl_transport_appends_events(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    transport = JsonlTransport(path)
    event = SemanticEvent.detected(
        source="fixture.camera.front",
        object_name="person",
        confidence=0.94,
        sequence=0,
        sensor_kind="image",
    )

    transport.publish(event.to_json())
    transport.publish(event.to_json())

    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 2
    assert rows[0]["type"] == "object.detected"
    assert rows[0]["object"] == "person"
