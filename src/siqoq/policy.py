from __future__ import annotations

from dataclasses import dataclass

from .events import SemanticEvent

#: Action Contract v0 version (docs/specs/action-contract.md). Bump on
#: breaking changes to `MockAction`'s required fields or `decide()`'s
#: signature; additive fields do not require a bump.
CONTRACT_VERSION = 0

#: D1: mock-only by construction. No actuator client exists in this module or
#: anywhere else in the package; extending this to a real actuator is a design
#: change requiring an explicit safety review (see AGENTS.md "Engineering rules").
_ACTION_BY_TYPE = {
    "object.detected": "log_detection",
}
_DEFAULT_ACTION = "noop"


@dataclass(slots=True, frozen=True)
class MockAction:
    """Action Contract v0 output envelope.

    ``mock`` is the safety-sensitive field of this contract: it is
    REVIEWED and pinned to ``True`` for every producer in this codebase
    (see D1 above and docs/specs/action-contract.md "Safety review"). A
    future real-actuator adapter MUST NOT flip this default silently; doing
    so is a design change requiring explicit safety sign-off.
    """

    action: str
    event_type: str
    mock: bool = True


@dataclass(slots=True, frozen=True)
class SafetyGate:
    """Authoritative mock-only safety boundary for action decisions."""

    allow_mock_actions: bool = True

    def approve(self, action: str) -> bool:
        return self.allow_mock_actions and action != _DEFAULT_ACTION


def decide(
    event: SemanticEvent,
    *,
    minimum_confidence: float = 0.0,
    safety_gate: SafetyGate | None = None,
) -> MockAction:
    """Deterministically map a SemanticEvent to a mock action decision.

    Pure function of the event's ``type`` only, so identical input always
    yields identical output and no real actuator is ever invoked.
    """
    if not 0 <= minimum_confidence <= 1:
        raise ValueError("minimum_confidence must be between 0 and 1")
    action = _ACTION_BY_TYPE.get(event.type, _DEFAULT_ACTION)
    if event.confidence < minimum_confidence:
        action = _DEFAULT_ACTION
    if safety_gate is not None and not safety_gate.approve(action):
        action = _DEFAULT_ACTION
    return MockAction(action=action, event_type=event.type)
