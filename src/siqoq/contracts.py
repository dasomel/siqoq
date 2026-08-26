from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True, slots=True)
class SensorSample:
    """Vendor-neutral input captured from a simulated or physical sensor."""

    source: str
    kind: str
    timestamp: str
    sequence: int
    payload: Any = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Detection:
    """Normalized perception result independent from an inference vendor."""

    label: str
    confidence: float
    attributes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ActionRequest:
    """Intent to interact with the physical world before safety evaluation."""

    action: str
    target: str
    parameters: Mapping[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None


@dataclass(frozen=True, slots=True)
class ActionResult:
    """Result returned by an action adapter."""

    accepted: bool
    action: str
    target: str
    status: str
    detail: str = ""
    correlation_id: str | None = None


@dataclass(frozen=True, slots=True)
class DeviceCapabilities:
    """Minimal runtime capability description used for portable placement."""

    architecture: str
    accelerator: str | None = None
    sensors: Sequence[str] = ()
    actuators: Sequence[str] = ()


class SensorAdapter(Protocol):
    def read(self) -> SensorSample | None: ...


class InferenceAdapter(Protocol):
    def infer(self, sample: SensorSample) -> Sequence[Detection]: ...


class EventTransport(Protocol):
    def publish(self, event_json: str) -> None: ...


class Policy(Protocol):
    def decide(self, events: Sequence[Any]) -> Sequence[ActionRequest]: ...


class SafetyGate(Protocol):
    def evaluate(self, request: ActionRequest) -> tuple[bool, str]: ...


class ActionAdapter(Protocol):
    def execute(self, request: ActionRequest) -> ActionResult: ...
