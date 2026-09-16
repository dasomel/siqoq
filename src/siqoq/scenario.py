from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .policy import decide
from .sensors import FixtureSensorAdapter, GeneratedSensorAdapter, SensorAdapter


@dataclass(slots=True, frozen=True)
class ScenarioConfig:
    """Runtime configuration for a hardware-free scenario run.

    ``adapter`` selects the sensor source: "generated" for the synthetic demo
    behavior, or "fixture" to read recorded samples from ``source_path``.
    """

    adapter: str
    steps: int
    source_path: str | None = None
    output_path: str | None = None

    @classmethod
    def from_json(cls, path: str | Path) -> ScenarioConfig:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            adapter=data["adapter"],
            steps=data["steps"],
            source_path=data.get("source_path"),
            output_path=data.get("output_path"),
        )

    def build_adapter(self) -> SensorAdapter:
        if self.adapter == "generated":
            return GeneratedSensorAdapter()
        if self.adapter == "fixture":
            if not self.source_path:
                raise ValueError("fixture adapter requires source_path")
            return FixtureSensorAdapter(path=Path(self.source_path))
        raise ValueError(f"unknown adapter: {self.adapter!r}")


@dataclass(slots=True, frozen=True)
class ScenarioSummary:
    event_count: int
    type_counts: dict[str, int]
    sequence_hash: str

    def to_json(self) -> str:
        return json.dumps(
            {
                "event_count": self.event_count,
                "type_counts": self.type_counts,
                "sequence_hash": self.sequence_hash,
            },
            ensure_ascii=False,
            sort_keys=True,
        )


def _sequence_hash(payloads: list[str]) -> str:
    digest = hashlib.sha256()
    for payload in payloads:
        digest.update(payload.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def run_scenario(config: ScenarioConfig) -> ScenarioSummary:
    """Run a scenario end-to-end: read events, apply the mock policy, emit output.

    Writes each SemanticEvent as one JSONL line to ``config.output_path`` when
    set, and returns a machine-readable summary for regression assertions.
    """
    adapter = config.build_adapter()
    payloads: list[str] = []
    type_counts: Counter[str] = Counter()

    output_handle = (
        Path(config.output_path).open("w", encoding="utf-8") if config.output_path else None
    )
    try:
        for event in adapter.read(count=config.steps):
            decide(event)  # exercise the mock, safety-gated policy path
            payload = event.to_json()
            payloads.append(payload)
            type_counts[event.type] += 1
            if output_handle is not None:
                output_handle.write(payload + "\n")
    finally:
        if output_handle is not None:
            output_handle.close()

    return ScenarioSummary(
        event_count=len(payloads),
        type_counts=dict(type_counts),
        sequence_hash=_sequence_hash(payloads),
    )
