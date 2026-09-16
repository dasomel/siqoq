from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .events import SemanticEvent


class SensorAdapter(Protocol):
    """Yields SemanticEvent samples regardless of whether the source is simulated or physical."""

    def read(self, *, count: int) -> Iterator[SemanticEvent]: ...


@dataclass(slots=True, frozen=True)
class SensorSample:
    """Normalized, line-oriented fixture sample."""

    timestamp: str
    source: str
    object: str
    confidence: float
    type: str = "object.detected"

    @classmethod
    def from_record(cls, record: object, *, line_number: int) -> SensorSample:
        if not isinstance(record, dict):
            raise ValueError(f"line {line_number}: expected a JSON object")
        required = ("timestamp", "source", "object", "confidence")
        missing = [key for key in required if key not in record]
        if missing:
            raise ValueError(f"line {line_number}: missing fields: {', '.join(missing)}")
        text_fields = ("timestamp", "source", "object")
        if not all(isinstance(record[key], str) and record[key] for key in text_fields):
            raise ValueError(
                f"line {line_number}: timestamp, source, and object must be non-empty strings"
            )
        confidence = record["confidence"]
        if (
            isinstance(confidence, bool)
            or not isinstance(confidence, (int, float))
            or not 0 <= confidence <= 1
        ):
            raise ValueError(f"line {line_number}: confidence must be a number between 0 and 1")
        event_type = record.get("type", "object.detected")
        if not isinstance(event_type, str) or not event_type:
            raise ValueError(f"line {line_number}: type must be a non-empty string")
        return cls(
            record["timestamp"], record["source"], record["object"], float(confidence), event_type
        )

    def to_event(self) -> SemanticEvent:
        return SemanticEvent(self.type, self.source, self.object, self.confidence, self.timestamp)


@dataclass(slots=True)
class GeneratedSensorAdapter:
    """Wraps today's synthetic demo behavior behind the SensorAdapter interface."""

    source: str = "sim.camera.front"
    object_name: str = "person"
    confidence: float = 0.94
    timestamp: str | None = None

    def read(self, *, count: int) -> Iterator[SemanticEvent]:
        for _ in range(count):
            if self.timestamp is None:
                yield SemanticEvent.detected(
                    source=self.source,
                    object_name=self.object_name,
                    confidence=self.confidence,
                )
            else:
                yield SemanticEvent(
                    type="object.detected",
                    source=self.source,
                    object=self.object_name,
                    confidence=self.confidence,
                    timestamp=self.timestamp,
                )


@dataclass(slots=True)
class FixtureSensorAdapter:
    """Reads a sequence of recorded sensor samples from a JSONL fixture file."""

    path: Path

    def read(self, *, count: int) -> Iterator[SemanticEvent]:
        with self.path.open(encoding="utf-8") as handle:
            emitted = 0
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                if emitted >= count:
                    break
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"line {line_number}: invalid JSON: {exc.msg}") from exc
                yield SensorSample.from_record(record, line_number=line_number).to_event()
                emitted += 1
