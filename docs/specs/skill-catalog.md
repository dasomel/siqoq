# Skill Catalog v0

Status: v0 (`src/siqoq/skills.py`).

The skill catalog maps existing `SemanticEvent.type` values (see
`docs/specs/semantic-event-contract.md`) to named "skills" — capabilities a
runtime/agent can advertise it handles. This is the foundation for future
skill-based routing/agent integration (issue #63, part of #11).

## Data model

```python
@dataclass(frozen=True, slots=True)
class SkillDefinition:
    name: str
    event_types: tuple[str, ...]
    description: str
```

- `name: str` — the skill's identifier, e.g. `"object-detection"`.
- `event_types: tuple[str, ...]` — the `SemanticEvent.type` values this
  skill handles.
- `description: str` — human-readable summary.

## Built-in catalog

`list_catalog()` returns the built-in registry. Today it contains a single
entry that matches the only event type produced anywhere in this codebase
(`SemanticEvent.detected()` always sets `type="object.detected"`):

```python
SkillDefinition(
    name="object-detection",
    event_types=("object.detected",),
    description="Detects and classifies objects in a frame",
)
```

No speculative event types are invented here; new skills are added only as
new event types are actually introduced elsewhere in the codebase.

## Lookup

```python
def classify(event: SemanticEvent) -> list[str]:
    ...
```

Returns the names of all catalog skills whose `event_types` include
`event.type`, in catalog definition order. Returns an empty list when no
skill matches. Lookup is deterministic — it depends only on `event.type`
and the static catalog contents.

## CLI

```
siqoq skills list
siqoq skills classify --event-type object.detected
```

`list` prints the catalog as JSON; `classify` prints a JSON array of
matching skill names (empty array `[]` when nothing matches).

## Explicit non-goals / scope

- **This catalog is data, not a new event schema.** It does not add,
  remove, or rename any field on `SemanticEvent`, and it does not change
  `REQUIRED_FIELDS`, `OPTIONAL_FIELDS`, or `SCHEMA_VERSION` in
  `siqoq.events`. Adding, removing, or editing catalog entries is a data
  change, not a schema/contract change.
- It does not implement routing, dispatch, or agent invocation — it only
  answers "which skill names match this event," leaving what to do with
  that answer to future work.
