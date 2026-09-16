# Deterministic scenario fixtures

Siqoq's hardware-free scenario runner accepts JSONL sensor fixtures. Each
non-empty line is one sample and must contain:

```json
{"timestamp":"2026-01-01T00:00:00+00:00","source":"sim.camera.front","object":"person","confidence":0.94,"type":"object.detected"}
```

`timestamp`, `source`, `object`, and `confidence` are required. `type` is
optional and defaults to `object.detected`; confidence is a number in the
inclusive range 0–1. Blank lines are ignored, and samples retain file order.
Malformed JSON or invalid fields raise an error containing the 1-based input
line number. The adapter emits the same `SemanticEvent` shape as the
generated sensor adapter.

The deterministic policy is mock-only. It maps `object.detected` to
`log_detection`, applies an optional minimum confidence threshold, and can be
disabled by `SafetyGate`. A disabled gate or a failed threshold returns
`noop`; no physical actuator is reachable from this path.

Run the regression path with:

```console
siqoq scenario run --config examples/scenario.json
```

The command emits a sorted JSON summary containing event count, event type
counts, and a SHA-256 hash of the emitted event sequence. The fixture path is
therefore suitable for CI assertions and future simulation adapters.
