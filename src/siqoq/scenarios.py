from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

from .adapters import AllowListSafetyGate, MemoryTransport, MockActionAdapter, StaticInference
from .contracts import ActionRequest, Policy, SensorSample
from .events import SemanticEvent
from .pipeline import SiqoqPipeline
from .runtime import discover_capabilities


class JsonlFixtureSensor:
    """Read normalized SensorSample rows from a deterministic JSONL fixture."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._samples = self._load()
        self._index = 0

    def _load(self) -> list[SensorSample]:
        samples: list[SensorSample] = []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        for line_number, raw_line in enumerate(lines, 1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at line {line_number}: {exc.msg}") from exc
            samples.append(
                SensorSample(
                    source=str(row["source"]),
                    kind=str(row["kind"]),
                    timestamp=str(row["timestamp"]),
                    sequence=int(row["sequence"]),
                    payload=row.get("payload"),
                    metadata=row.get("metadata", {}),
                )
            )
        return samples

    def read(self) -> SensorSample | None:
        if self._index >= len(self._samples):
            return None
        sample = self._samples[self._index]
        self._index += 1
        return sample


@dataclass(frozen=True, slots=True)
class DetectionRulePolicy(Policy):
    """Deterministic policy for CI scenarios; safety gate remains authoritative."""

    object_name: str = "person"
    minimum_confidence: float = 0.8
    action: str = "indicator.on"
    target: str = "demo.indicator"

    def decide(self, events: Sequence[SemanticEvent]) -> Sequence[ActionRequest]:
        for event in events:
            if event.object == self.object_name and event.confidence >= self.minimum_confidence:
                return (
                    ActionRequest(
                        action=self.action,
                        target=self.target,
                        correlation_id=event.event_id,
                    ),
                )
        return ()


@dataclass(frozen=True, slots=True)
class ScenarioSummary:
    name: str
    samples: int
    events: int
    actions: int
    rejected_actions: int
    architecture: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, separators=(",", ":"))


def run_fixture_scenario(path: str | Path, *, name: str = "fixture") -> ScenarioSummary:
    sensor = JsonlFixtureSensor(path)
    transport = MemoryTransport()
    action = MockActionAdapter()
    pipeline = SiqoqPipeline(
        sensor=sensor,
        inference=StaticInference(),
        transport=transport,
        policy=DetectionRulePolicy(),
        safety=AllowListSafetyGate(allowed_actions=frozenset({"indicator.on"})),
        action=action,
    )

    sample_count = 0
    event_count = 0
    action_count = 0
    rejected_count = 0
    while True:
        result = pipeline.run_once()
        if not result.events and not result.action_results:
            break
        sample_count += 1
        event_count += len(result.events)
        action_count += len(result.action_results)
        rejected_count += sum(not item.accepted for item in result.action_results)

    return ScenarioSummary(
        name=name,
        samples=sample_count,
        events=event_count,
        actions=action_count,
        rejected_actions=rejected_count,
        architecture=discover_capabilities().architecture,
    )
