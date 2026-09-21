from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .actuation import ActionResult
from .events import SemanticEvent

#: D1: metadata is redacted by default. `build_trace()` only copies
#: `event.metadata` onto the trace when the caller passes
#: `include_metadata=True`. This is deliberate: `metadata` is a free-form
#: dict (see events.py) and producers may stuff raw sensor payloads (e.g.
#: frame bytes) into it, which must never leak into a decision trace by
#: default (docs/specs/decision-trace.md "Redaction").


@dataclass(slots=True, frozen=True)
class DecisionTrace:
    """A single traceable record spanning event -> decision -> action.

    Correlates a :class:`SemanticEvent` with the :class:`ActionResult` that
    followed it (if any) by `correlation_id`. By default carries only
    type/source/confidence/timestamps/outcome — enough for RCA without
    leaking raw sensor payloads. Pass `include_metadata=True` to
    :func:`build_trace` for verbose debugging output that also carries the
    event's raw `metadata`.

    ``to_json()`` follows the same additive-only, omit-if-empty style as
    :meth:`siqoq.events.SemanticEvent.to_json`.
    """

    correlation_id: str | None
    event_type: str
    event_source: str
    event_confidence: float
    event_timestamp: str
    action: str | None
    action_outcome: str | None
    action_timestamp: str | None
    metadata: dict[str, Any] | None = None

    def to_json(self) -> str:
        payload = asdict(self)
        for key in ("correlation_id", "action", "action_outcome", "action_timestamp", "metadata"):
            if payload[key] is None:
                del payload[key]
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def build_trace(
    event: SemanticEvent,
    result: ActionResult | None = None,
    *,
    include_metadata: bool = False,
) -> DecisionTrace:
    """Assemble a :class:`DecisionTrace` from a `SemanticEvent` and an
    optional `ActionResult`.

    Carries the event's own fields plus whatever `result` is passed,
    correlated by `correlation_id` (the caller is trusted to pass a
    matching pair; this does not search for a match across arbitrary
    lists). `metadata` is redacted (left `None`) unless `include_metadata`
    is `True`.
    """
    return DecisionTrace(
        correlation_id=event.correlation_id,
        event_type=event.type,
        event_source=event.source,
        event_confidence=event.confidence,
        event_timestamp=event.timestamp,
        action=result.action if result is not None else None,
        action_outcome=result.outcome if result is not None else None,
        action_timestamp=result.timestamp if result is not None else None,
        metadata=(event.metadata or None) if include_metadata else None,
    )
