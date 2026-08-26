from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class SensorSample:
    """Vendor-neutral input captured from a simulated or physical sensor."""

    source: str
    kind: str
    timestamp: str
    sequence: int
    payload: Any = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("sensor source must not be empty")
        if not self.kind.strip():
            raise ValueError("sensor kind must not be empty")
        if not self.timestamp.strip():
            raise ValueError("sensor timestamp must not be empty")
        if self.sequence < 0:
            raise ValueError("sensor sequence must be >= 0")


@dataclass(frozen=True, slots=True)
class Detection:
    """Normalized perception result independent from an inference vendor."""

    label: str
    confidence: float
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("detection label must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("detection confidence must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class ActionRequest:
    """Intent to interact with the physical world before safety evaluation."""

    action: str
    target: str
    parameters: Mapping[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        if not self.action.strip():
            raise ValueError("action must not be empty")
        if not self.target.strip():
            raise ValueError("action target must not be empty")


@dataclass(frozen=True, slots=True)
class ActionResult:
    """Result returned by an action adapter."""

    accepted: bool
    action: str
    target: str
    status: str
    detail: str = ""
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        if not self.action.strip():
            raise ValueError("action result action must not be empty")
        if not self.target.strip():
            raise ValueError("action result target must not be empty")
        if not self.status.strip():
            raise ValueError("action result status must not be empty")


@dataclass(frozen=True, slots=True)
class DeviceCapabilities:
    """Minimal runtime capability description used for portable placement."""

    architecture: str
    accelerator: str | None = None
    sensors: Sequence[str] = ()
    actuators: Sequence[str] = ()

    def __post_init__(self) -> None:
        if not self.architecture.strip():
            raise ValueError("architecture must not be empty")


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
