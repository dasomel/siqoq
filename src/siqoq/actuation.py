from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Protocol

from .events import SemanticEvent
from .policy import _DEFAULT_ACTION, MockAction, SafetyGate, decide

#: D1: mock-only by construction. This module is the ONLY place `policy.decide()`
#: output is wired to something that "executes" an action, and the only
#: implementation (`MockActuatorAdapter`) never performs I/O or touches real
#: hardware. `policy.py` MUST NOT import this module (grep-verifiable; see
#: docs/specs/action-contract.md "Safety review" and AGENTS.md "Engineering
#: rules" on actuator authority). Adding a real-hardware adapter here is an
#: explicit, high-risk design change requiring separate authorization and is
#: intentionally left as a documented follow-up, not implemented.


@dataclass(slots=True, frozen=True)
class ActionResult:
    """Outcome of attempting to execute a :class:`~siqoq.policy.MockAction`.

    ``to_json()`` follows the same additive-only, omit-if-empty style as
    :meth:`siqoq.events.SemanticEvent.to_json`.
    """

    action: str
    event_type: str
    outcome: str
    correlation_id: str | None
    timestamp: str

    def to_json(self) -> str:
        payload = asdict(self)
        if payload["correlation_id"] is None:
            del payload["correlation_id"]
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


class ActuatorAdapter(Protocol):
    """Boundary between a `MockAction` decision and whatever "executes" it."""

    def execute(self, action: MockAction) -> ActionResult: ...


class MockActuatorAdapter:
    """The only `ActuatorAdapter` implementation. No I/O, no side effects.

    Returns ``outcome="executed"`` only when ``action.mock is True`` and the
    action is not the default no-op action; otherwise returns ``"rejected"``
    (mock=False, never produced by `decide()` today, see action-contract.md)
    or ``"noop"`` (the default no-op action).
    """

    def execute(self, action: MockAction) -> ActionResult:
        if not action.mock:
            outcome = "rejected"
        elif action.action == _DEFAULT_ACTION:
            outcome = "noop"
        else:
            outcome = "executed"
        return ActionResult(
            action=action.action,
            event_type=action.event_type,
            outcome=outcome,
            correlation_id=None,
            timestamp=datetime.now(UTC).isoformat(),
        )


def decide_and_execute(
    event: SemanticEvent,
    *,
    adapter: ActuatorAdapter,
    minimum_confidence: float = 0.0,
    safety_gate: SafetyGate | None = None,
) -> ActionResult:
    """Wire `policy.decide()` to an `ActuatorAdapter`.

    This is the ONLY place in the codebase that connects a policy decision
    to something that "executes" it; `policy.py` itself has no knowledge of
    actuation.
    """
    action = decide(event, minimum_confidence=minimum_confidence, safety_gate=safety_gate)
    result = adapter.execute(action)
    return ActionResult(
        action=result.action,
        event_type=result.event_type,
        outcome=result.outcome,
        correlation_id=event.correlation_id,
        timestamp=result.timestamp,
    )
