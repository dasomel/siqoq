from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
import json
from typing import Any, Mapping
from uuid import uuid4


@dataclass(slots=True)
class SemanticEvent:
    type: str
    source: str
    object: str
    confidence: float
    timestamp: str
    event_id: str = field(default_factory=lambda: str(uuid4()))
    schema_version: str = "0.1"
    sequence: int | None = None
    sensor_kind: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def detected(
        cls,
        *,
        source: str,
        object_name: str,
        confidence: float,
        sequence: int | None = None,
        sensor_kind: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "SemanticEvent":
        return cls(
            type="object.detected",
            source=source,
            object=object_name,
            confidence=confidence,
            timestamp=datetime.now(UTC).isoformat(),
            sequence=sequence,
            sensor_kind=sensor_kind,
            metadata=metadata or {},
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, separators=(",", ":"))
