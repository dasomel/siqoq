from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from . import telemetry

#: Current schema version for :class:`SemanticEvent`. Bump on breaking changes
#: (removing/renaming a required field). Additive, backward-compatible fields
#: do not require a bump.
SCHEMA_VERSION = 1

#: Required fields carried by every semantic event, independent of type.
REQUIRED_FIELDS = ("type", "source", "object", "confidence", "timestamp", "schema_version")

#: Optional fields available on the envelope. Consumers must tolerate missing
#: or additional optional fields without failing.
OPTIONAL_FIELDS = ("correlation_id", "metadata")

_events_emitted_counter = telemetry.get_events_emitted_counter()


@dataclass(slots=True)
class SemanticEvent:
    """Versioned semantic event envelope.

    Required fields: type, source, object, confidence, timestamp, schema_version.
    Optional fields: correlation_id (for tracing a detection across stages),
    metadata (free-form dict for vendor-agnostic extra context).

    `to_json()` output is additive-only across schema versions: existing keys
    keep their meaning and position is not guaranteed, but old consumers that
    read specific keys continue to work.
    """

    type: str
    source: str
    object: str
    confidence: float
    timestamp: str
    schema_version: int = SCHEMA_VERSION
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def detected(
        cls,
        *,
        source: str,
        object_name: str,
        confidence: float,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SemanticEvent:
        event = cls(
            type="object.detected",
            source=source,
            object=object_name,
            confidence=confidence,
            timestamp=datetime.now(UTC).isoformat(),
            correlation_id=correlation_id,
            metadata=metadata or {},
        )
        _events_emitted_counter.add(1, {"source": source, "type": event.type})
        return event

    def to_json(self) -> str:
        payload = asdict(self)
        if payload["correlation_id"] is None:
            del payload["correlation_id"]
        if not payload["metadata"]:
            del payload["metadata"]
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
