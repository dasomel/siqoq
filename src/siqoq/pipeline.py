from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .contracts import (
    ActionAdapter,
    ActionRequest,
    ActionResult,
    EventTransport,
    InferenceAdapter,
    Policy,
    SafetyGate,
    SensorAdapter,
)
from .events import SemanticEvent


@dataclass
class NoOpPolicy(Policy):
    """Default policy that performs no physical action."""

    def decide(self, events: Sequence[SemanticEvent]) -> Sequence[ActionRequest]:
        return ()


@dataclass
class PipelineResult:
    events: list[SemanticEvent]
    action_results: list[ActionResult]


@dataclass
class SiqoqPipeline:
    sensor: SensorAdapter
    inference: InferenceAdapter
    transport: EventTransport
    policy: Policy
    safety: SafetyGate
    action: ActionAdapter

    def run_once(self) -> PipelineResult:
        sample = self.sensor.read()
        if sample is None:
            return PipelineResult(events=[], action_results=[])

        events = [
            SemanticEvent.detected(
                source=sample.source,
                object_name=detection.label,
                confidence=detection.confidence,
                sequence=sample.sequence,
                sensor_kind=sample.kind,
            )
            for detection in self.inference.infer(sample)
        ]

        for event in events:
            self.transport.publish(event.to_json())

        results: list[ActionResult] = []
        for request in self.policy.decide(events):
            allowed, reason = self.safety.evaluate(request)
            if not allowed:
                results.append(
                    ActionResult(
                        accepted=False,
                        action=request.action,
                        target=request.target,
                        status="rejected",
                        detail=reason,
                        correlation_id=request.correlation_id,
                    )
                )
                continue
            results.append(self.action.execute(request))

        return PipelineResult(events=events, action_results=results)
