from __future__ import annotations

from dataclasses import dataclass

from .events import SemanticEvent


@dataclass(frozen=True, slots=True)
class SkillDefinition:
    """A named capability a runtime/agent can advertise it handles.

    This is a data registry, not a new event schema: it maps existing
    `SemanticEvent.type` values (see docs/specs/semantic-event-contract.md)
    to a human-readable skill name. It does not change `SemanticEvent`'s
    required fields.
    """

    name: str
    event_types: tuple[str, ...]
    description: str


#: Built-in skill catalog. Only references event types that actually exist
#: today (`SemanticEvent.detected()` always produces "object.detected") —
#: no speculative event types are invented here.
_CATALOG: tuple[SkillDefinition, ...] = (
    SkillDefinition(
        name="object-detection",
        event_types=("object.detected",),
        description="Detects and classifies objects in a frame",
    ),
)


def list_catalog() -> list[SkillDefinition]:
    """Return the built-in skill catalog."""
    return list(_CATALOG)


def classify(event: SemanticEvent) -> list[str]:
    """Return the names of all catalog skills whose event_types include event.type.

    Deterministic: iterates the catalog in definition order and depends only
    on `event.type`. Returns an empty list when no skill matches.
    """
    return [skill.name for skill in _CATALOG if event.type in skill.event_types]
