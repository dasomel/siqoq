"""Pluggable event transport adapters for :class:`siqoq.events.SemanticEvent`.

The transport layer is the boundary between the semantic event contract and
whatever moves those events off-box (in-process queue, stdout, a file, NATS,
MQTT, ...). `EventPublisher`, `InMemoryTransport`, `StdoutTransport`, and
`FileTransport` are core, zero-dependency building blocks. NATS/MQTT
adapters are optional extras: their client libraries are imported lazily so
importing this module, and the base install/test suite, never requires
``nats-py`` or ``paho-mqtt``.

Install extras with ``pip install .[transport]``.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Protocol, runtime_checkable

from .events import SemanticEvent


@runtime_checkable
class EventPublisher(Protocol):
    """Minimal contract every transport adapter must satisfy.

    A publisher only needs to accept a `SemanticEvent` and deliver its JSON
    payload somewhere. Connection lifecycle (open/close) is adapter-specific
    and handled outside this protocol so mocks and in-process transports
    don't need to implement it.
    """

    def publish(self, event: SemanticEvent, *, subject: str | None = None) -> None:
        """Publish `event`. `subject` overrides any adapter default topic/subject."""
        ...


class InMemoryTransport:
    """Stdlib-only mock transport for hardware/service-free tests and local dev.

    Stores published events in order so tests can assert on delivery without
    a real broker.
    """

    def __init__(self, default_subject: str = "siqoq.events") -> None:
        self.default_subject = default_subject
        self.published: list[tuple[str, SemanticEvent]] = []

    def publish(self, event: SemanticEvent, *, subject: str | None = None) -> None:
        self.published.append((subject or self.default_subject, event))

    def clear(self) -> None:
        self.published.clear()


class StdoutTransport:
    """Writes each event as a JSON line to a stream (stdout by default)."""

    def __init__(self, stream: object | None = None) -> None:
        self._stream = stream if stream is not None else sys.stdout

    def publish(self, event: SemanticEvent, *, subject: str | None = None) -> None:
        del subject  # stdout has no addressable subject/topic
        print(event.to_json(), file=self._stream)  # type: ignore[arg-type]


class FileTransport:
    """Appends each event as a JSON line to a file (JSON Lines format)."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def publish(self, event: SemanticEvent, *, subject: str | None = None) -> None:
        del subject  # a single append-only file has no addressable subject
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(event.to_json())
            fh.write("\n")


class NatsTransport:
    """NATS-backed publisher. Requires the `transport` extra (`nats-py`).

    Uses a caller-supplied already-connected `nats.aio.client.Client`, kept
    out of this constructor so this module never has to manage an event
    loop itself; call sites own connection lifecycle.
    """

    def __init__(self, client: object, default_subject: str = "siqoq.events") -> None:
        try:
            import nats  # noqa: F401
        except ImportError as exc:  # pragma: no cover - exercised only without extra
            raise RuntimeError(
                "NatsTransport requires the 'transport' extra: pip install '.[transport]'"
            ) from exc
        self._client = client
        self.default_subject = default_subject

    async def publish_async(self, event: SemanticEvent, *, subject: str | None = None) -> None:
        payload = event.to_json().encode()
        await self._client.publish((subject or self.default_subject).encode(), payload)

    def publish(self, event: SemanticEvent, *, subject: str | None = None) -> None:
        raise RuntimeError("NatsTransport is async-only; use publish_async")


class MqttTransport:
    """MQTT-backed publisher. Requires the `transport` extra (`paho-mqtt`).

    Wraps a caller-supplied already-connected `paho.mqtt.client.Client`;
    this module never owns broker connection/reconnect policy.
    """

    def __init__(self, client: object, default_subject: str = "siqoq/events") -> None:
        try:
            import paho.mqtt.client  # noqa: F401
        except ImportError as exc:  # pragma: no cover - exercised only without extra
            raise RuntimeError(
                "MqttTransport requires the 'transport' extra: pip install '.[transport]'"
            ) from exc
        self._client = client
        self.default_subject = default_subject

    def publish(self, event: SemanticEvent, *, subject: str | None = None) -> None:
        self._client.publish(subject or self.default_subject, event.to_json())
