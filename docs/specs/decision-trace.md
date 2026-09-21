# Decision Trace v0

Status: v0 (`src/siqoq/trace.py`, part of #11).

`DecisionTrace` assembles a single traceable record spanning
sensor input -> semantic event -> policy decision -> action result, using
the existing `correlation_id` plumbing already carried by
`SemanticEvent` (`events.py`) and `ActionResult` (`actuation.py`). It is a
read-only view over data already produced elsewhere in the pipeline — it
does not observe sensors, run policy, or execute actions itself.

## Fields

```python
@dataclass(slots=True, frozen=True)
class DecisionTrace:
    correlation_id: str | None
    event_type: str
    event_source: str
    event_confidence: float
    event_timestamp: str
    action: str | None
    action_outcome: str | None
    action_timestamp: str | None
    metadata: dict[str, Any] | None = None
```

`build_trace(event, result=None, *, include_metadata=False)` constructs a
trace from a `SemanticEvent` and an optional `ActionResult`. It correlates
by `correlation_id` in the sense that both come from the caller as an
already-matched pair (e.g. the same pipeline run); it does not search a
list of events/results for a match — callers that need matching across a
log of many events/results must do that lookup themselves before calling
`build_trace()`.

## Redaction (default)

**By default (`include_metadata=False`), `DecisionTrace.metadata` is
always `None`, even when `event.metadata` has content.** This is the
redaction default required by the issue: `SemanticEvent.metadata` is a
free-form dict, and a producer could put a raw sensor payload (e.g. a
camera frame, a raw audio buffer) in it. A decision trace is meant to be
readable, shareable, and safe to log for RCA — it must never carry that
raw payload along for the ride.

The default trace therefore only contains:

- `event_type`, `event_source`, `event_confidence`, `event_timestamp` —
  what was detected, by what, at what confidence and when;
- `action`, `action_outcome`, `action_timestamp` — what action followed,
  what happened to it (`"executed"` / `"rejected"` / `"noop"`, per
  `actuation.py`), and when;
- `correlation_id` — to tie this trace back to the originating event/action
  pair in other logs.

This is deliberately enough context to do root-cause analysis (what was
seen, how confident, what the system decided to do, and the outcome)
without ever including raw sensor bytes.

## Verbose opt-in

Passing `include_metadata=True` to `build_trace()` copies `event.metadata`
onto `DecisionTrace.metadata` verbatim. This is explicitly a verbose,
non-default debugging mode: a caller (human operator or debugging tool)
that opts in is accepting that any raw/sensitive data a producer put in
`metadata` will appear in the resulting trace and in whatever the trace is
logged/printed to. Do not enable this in default logging paths.

## `to_json()`

Follows the same additive-only, omit-if-empty-optional convention as
`SemanticEvent.to_json()` / `ActionResult.to_json()`: `correlation_id`,
`action`, `action_outcome`, `action_timestamp`, and `metadata` are omitted
from the JSON payload when `None`.

## CLI

```
siqoq trace build --event-json <path> [--action-json <path>] [--include-metadata]
```

Reads a `SemanticEvent` JSON document (and, optionally, an `ActionResult`
JSON document) and prints the built `DecisionTrace` as JSON. `--include-metadata`
enables the verbose opt-in above.

## Compatibility rules

- **Breaking**: removing/renaming a `DecisionTrace` field, or changing the
  default of `include_metadata` away from `False` (that default is the
  redaction guarantee this contract exists to make).
- **Compatible / additive**: adding a new optional `DecisionTrace` field
  with a default, or adding new optional keyword parameters to
  `build_trace()`.
