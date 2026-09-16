from __future__ import annotations

from dataclasses import dataclass

from .events import SemanticEvent

#: D1: mock-only by construction. No actuator client exists in this module or
#: anywhere else in the package; extending this to a real actuator is a design
#: change requiring an explicit safety review (see AGENTS.md "Engineering rules").
_ACTION_BY_TYPE = {
    "object.detected": "log_detection",
}
_DEFAULT_ACTION = "noop"


@dataclass(slots=True, frozen=True)
class MockAction:
    action: str
    event_type: str
    mock: bool = True


def decide(event: SemanticEvent) -> MockAction:
    """Deterministically map a SemanticEvent to a mock action decision.

    Pure function of the event's ``type`` only, so identical input always
    yields identical output and no real actuator is ever invoked.
    """
    action = _ACTION_BY_TYPE.get(event.type, _DEFAULT_ACTION)
    return MockAction(action=action, event_type=event.type)
