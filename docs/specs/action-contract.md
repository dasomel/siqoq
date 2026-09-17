# Action Contract v0

Status: v0 (`CONTRACT_VERSION = 0` in `siqoq.policy`).

`MockAction` is the output of `siqoq.policy.decide()`, the boundary between
policy/decision logic and action adapters (see `docs/architecture.md`,
"Action adapters").

## Fields

```python
@dataclass(slots=True, frozen=True)
class MockAction:
    action: str
    event_type: str
    mock: bool = True
```

- `action: str` — the decided action name (`"log_detection"`, `"noop"`, or
  future values from `_ACTION_BY_TYPE`).
- `event_type: str` — the `SemanticEvent.type` that produced this decision.
- `mock: bool` — **safety-sensitive field, explicitly reviewed** (see below).

## Safety review (explicit)

This is the explicit safety review required by AGENTS.md's rule that
actuator behavior is a design change:

- `mock` defaults to `True` and, as of this contract version, is never set
  to `False` anywhere in this codebase. `decide()` is a pure function of
  `SemanticEvent.type`/`confidence` plus the optional `SafetyGate`; no
  actuator client, network call, or GPIO/relay/motor driver exists in
  `siqoq.policy` or is reachable from it (grep-verifiable: no `import` of a
  hardware/actuator SDK in this module).
- `SafetyGate.approve()` is the authoritative gate: it can only downgrade an
  action to `_DEFAULT_ACTION` ("noop"); it has no code path that upgrades or
  bypasses `mock`.
- **Reviewed conclusion**: v0 of this contract is safe by construction for
  any deployment — there is no execution path from `decide()`'s output to a
  physical actuator. A future adapter that consumes `MockAction` and drives
  real hardware, or a change that allows `mock=False`, is explicitly
  declared here as a breaking, high-risk design change requiring its own
  safety review, tests, and AGENTS.md-level sign-off before merge — not
  something `decide()`/`MockAction` should absorb silently.

## Compatibility rules

- **Breaking** (`CONTRACT_VERSION` bump required): removing/renaming a
  `MockAction` field, changing `mock`'s default or allowing `False` from
  `decide()`, or changing `decide()`'s parameter contract (e.g. removing
  `minimum_confidence`/`safety_gate`).
- **Compatible / additive** (no bump): adding a new optional
  `MockAction` field with a default, adding new `_ACTION_BY_TYPE` mappings,
  or adding new optional keyword parameters to `decide()`.

## Conformance

`decide()` is deterministic and pure (same `SemanticEvent` + parameters ->
same `MockAction`), which is exercised by `tests/test_policy.py` (existing)
and covered by the same "no vendor/actuator type" check applied to
`sensors.py`/`events.py`.
