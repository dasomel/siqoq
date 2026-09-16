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
            lines = [line for line in handle if line.strip()]

        for line in lines[:count]:
            record = json.loads(line)
            yield SemanticEvent(
                type=record["type"],
                source=record["source"],
                object=record["object"],
                confidence=record["confidence"],
                timestamp=record["timestamp"],
            )
