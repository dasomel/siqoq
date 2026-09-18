from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .events import SemanticEvent

#: Sensor Contract v0 version. Bump on breaking changes to the `SensorAdapter`
#: method signature or its documented event-shape guarantees (see
#: docs/specs/sensor-contract.md). Additive, backward-compatible changes
#: (e.g. a new optional method with a default) do not require a bump.
CONTRACT_VERSION = 0


class SensorAdapter(Protocol):
    """Sensor Contract v0 (event-level layer): yields SemanticEvent samples
    regardless of whether the source is simulated or physical.

    This is the higher, event-level sensor contract. `siqoq.video_sensors`
    defines a lower, frame-level contract (`FrameSensor`) for sources that
    hand back raw frames instead of semantic events; a `FrameSensor` is
    typically composed with an `InferenceAdapter` to produce the
    `SemanticEvent`s this protocol yields. See docs/specs/sensor-contract.md
    for the full contract and how the two layers relate.
    """

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
    """Wraps today's synthetic demo behavior behind the SensorAdapter interface.

    Reference simulation adapter for the Simulation Adapter Contract v0
    (docs/specs/simulation-adapter-contract.md): a `SensorAdapter`
    specialization for simulated/synthetic sources, distinguished from
    recorded/physical sources by provenance (callers SHOULD tag output
    ``metadata["provenance"] = PROVENANCE_SIMULATED``, see `siqoq.events`),
    not by a different interface.

    Satisfies the contract's determinism requirement: passing a fixed
    `timestamp` makes every event yielded by `read()` carry that exact
    value instead of ambient clock time, so two independent runs with the
    same construction parameters produce an identical, byte-for-byte
    reproducible event sequence (verified by
    `tests/test_sensors.py::test_adapter_is_deterministic_with_fixed_timestamp`
    and
    `test_generated_adapter_is_deterministic_and_simulated_provenance_ready`).
    Leaving `timestamp` unset falls back to ambient clock time via
    `SemanticEvent.detected()`, which is fine for demos but MUST NOT be
    relied upon for CI assertions.
    """

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
