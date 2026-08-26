from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Iterable, Sequence

from .contracts import (
    ActionAdapter,
    ActionRequest,
    ActionResult,
    Detection,
    EventTransport,
    InferenceAdapter,
    SafetyGate,
    SensorAdapter,
    SensorSample,
)


@dataclass
class GeneratedSensor(SensorAdapter):
    """Hardware-free deterministic sensor source for demos and CI."""

    source: str = "sim.camera.front"
    kind: str = "image"
    count: int = 1
    _sequence: int = 0

    def read(self) -> SensorSample | None:
        if self._sequence >= self.count:
            return None
        sample = SensorSample(
            source=self.source,
            kind=self.kind,
            timestamp=datetime.now(UTC).isoformat(),
            sequence=self._sequence,
            payload={"synthetic": True},
            metadata={"origin": "generated"},
        )
        self._sequence += 1
        return sample


@dataclass
class StaticInference(InferenceAdapter):
    """Deterministic perception adapter used until a real model runtime is attached."""

    detections: Sequence[Detection] = (
        Detection(label="person", confidence=0.94),
    )

    def infer(self, sample: SensorSample) -> Sequence[Detection]:
        return tuple(self.detections)


@dataclass
class MemoryTransport(EventTransport):
    """In-memory event sink for tests and local composition."""

    messages: list[str] = field(default_factory=list)

    def publish(self, event_json: str) -> None:
        self.messages.append(event_json)


@dataclass
class AllowListSafetyGate(SafetyGate):
    """Minimal safe-by-default gate for skeleton action flows."""

    allowed_actions: frozenset[str] = frozenset()

    def evaluate(self, request: ActionRequest) -> tuple[bool, str]:
        if request.action not in self.allowed_actions:
            return False, f"action '{request.action}' is not allow-listed"
        return True, "allowed"


@dataclass
class MockActionAdapter(ActionAdapter):
    """Action adapter that never touches hardware."""

    executed: list[ActionRequest] = field(default_factory=list)

    def execute(self, request: ActionRequest) -> ActionResult:
        self.executed.append(request)
        return ActionResult(
            accepted=True,
            action=request.action,
            target=request.target,
            status="mock-executed",
            detail="no physical hardware was touched",
            correlation_id=request.correlation_id,
        )


def collect_samples(sensor: SensorAdapter) -> Iterable[SensorSample]:
    while True:
        sample = sensor.read()
        if sample is None:
            return
        yield sample
