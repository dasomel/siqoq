from collections.abc import Sequence
from dataclasses import dataclass

from siqoq.adapters import (
    AllowListSafetyGate,
    GeneratedSensor,
    MemoryTransport,
    MockActionAdapter,
    StaticInference,
)
from siqoq.contracts import ActionRequest
from siqoq.events import SemanticEvent
from siqoq.pipeline import SiqoqPipeline


@dataclass
class TriggerPolicy:
    def decide(self, events: Sequence[SemanticEvent]) -> Sequence[ActionRequest]:
        return (ActionRequest(action="relay.on", target="demo.relay"),)


def test_action_is_rejected_by_default() -> None:
    action = MockActionAdapter()
    pipeline = SiqoqPipeline(
        sensor=GeneratedSensor(count=1),
        inference=StaticInference(),
        transport=MemoryTransport(),
        policy=TriggerPolicy(),
        safety=AllowListSafetyGate(),
        action=action,
    )

    result = pipeline.run_once()

    assert len(result.action_results) == 1
    assert result.action_results[0].accepted is False
    assert result.action_results[0].status == "rejected"
    assert action.executed == []


def test_allow_list_permits_mock_action_only() -> None:
    action = MockActionAdapter()
    pipeline = SiqoqPipeline(
        sensor=GeneratedSensor(count=1),
        inference=StaticInference(),
        transport=MemoryTransport(),
        policy=TriggerPolicy(),
        safety=AllowListSafetyGate(allowed_actions=frozenset({"relay.on"})),
        action=action,
    )

    result = pipeline.run_once()

    assert result.action_results[0].accepted is True
    assert result.action_results[0].status == "mock-executed"
    assert len(action.executed) == 1
