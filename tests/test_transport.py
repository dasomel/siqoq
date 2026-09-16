from __future__ import annotations

import importlib.util
import json

import pytest

from siqoq.events import SemanticEvent
from siqoq.transport import (
    EventPublisher,
    FileTransport,
    InMemoryTransport,
    StdoutTransport,
)

HAS_NATS = importlib.util.find_spec("nats") is not None
HAS_MQTT = importlib.util.find_spec("paho") is not None and (
    importlib.util.find_spec("paho.mqtt.client") is not None
)


def _sample_event() -> SemanticEvent:
    return SemanticEvent.detected(source="sim.camera.front", object_name="person", confidence=0.94)


def test_in_memory_transport_publishes_in_order() -> None:
    transport = InMemoryTransport()
    event_a = _sample_event()
    event_b = _sample_event()

    transport.publish(event_a)
    transport.publish(event_b, subject="siqoq.custom")

    assert transport.published == [
        ("siqoq.events", event_a),
        ("siqoq.custom", event_b),
    ]


def test_in_memory_transport_clear() -> None:
    transport = InMemoryTransport()
    transport.publish(_sample_event())
    transport.clear()
    assert transport.published == []


def test_in_memory_transport_satisfies_event_publisher_protocol() -> None:
    assert isinstance(InMemoryTransport(), EventPublisher)


def test_stdout_transport_writes_json_line(capsys) -> None:
    transport = StdoutTransport()

    transport.publish(_sample_event())

    captured = capsys.readouterr()
    payload = json.loads(captured.out.strip())
    assert payload["type"] == "object.detected"
    assert payload["schema_version"] == 1


def test_file_transport_appends_json_lines(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    transport = FileTransport(path)

    transport.publish(_sample_event())
    transport.publish(_sample_event())

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    for line in lines:
        payload = json.loads(line)
        assert payload["object"] == "person"


@pytest.mark.skipif(not HAS_NATS, reason="nats-py extra not installed")
def test_nats_transport_requires_extra_when_missing() -> None:
    from siqoq.transport import NatsTransport

    NatsTransport(client=object())


@pytest.mark.skipif(HAS_NATS, reason="nats-py extra is installed")
def test_nats_transport_raises_without_extra() -> None:
    from siqoq.transport import NatsTransport

    with pytest.raises(RuntimeError, match="transport"):
        NatsTransport(client=object())


@pytest.mark.skipif(not HAS_MQTT, reason="paho-mqtt extra not installed")
def test_mqtt_transport_requires_extra_when_missing() -> None:
    from siqoq.transport import MqttTransport

    MqttTransport(client=object())


@pytest.mark.skipif(HAS_MQTT, reason="paho-mqtt extra is installed")
def test_mqtt_transport_raises_without_extra() -> None:
    from siqoq.transport import MqttTransport

    with pytest.raises(RuntimeError, match="transport"):
        MqttTransport(client=object())
