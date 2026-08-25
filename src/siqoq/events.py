from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json


@dataclass(slots=True)
class SemanticEvent:
    type: str
    source: str
    object: str
    confidence: float
    timestamp: str

    @classmethod
    def detected(
        cls,
        *,
        source: str,
        object_name: str,
        confidence: float,
    ) -> "SemanticEvent":
        return cls(
            type="object.detected",
            source=source,
            object=object_name,
            confidence=confidence,
            timestamp=datetime.now(UTC).isoformat(),
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, separators=(",", ":"))
