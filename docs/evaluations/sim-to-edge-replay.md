# Simulation-to-edge workflow replay

Status: verified for the current hardware-free MVP path (2026-09-17).

This replay validates the `siqoq-sim-to-edge-workflow` skill's laptop path:

```text
JSONL fixture sensor → normalized semantic event → mock policy/safety gate → JSONL transport output
```

## Fresh-session commands

From a clean checkout with Python 3.12:

```console
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
make verify
siqoq scenario run --config examples/scenario.json
```

Observed on macOS ARM64 with Python 3.12:

```text
39 passed, 3 skipped
{"event_count": 3, "sequence_hash": "25f893c180473bf3e429a034687ba64cafa19aca921162b4472c6012d37a2611", "type_counts": {"object.detected": 3}}
```

The regression suite also verifies that a missing fixture raises
`FileNotFoundError` before any event is emitted. Malformed JSON and invalid
confidence values include their 1-based input line number. The policy path is
mock-only and a disabled `SafetyGate` returns `noop`; it cannot invoke a
physical actuator.

CI preserves the pytest XML report, scenario summary, and JSONL event stream
as the `siqoq-simulation-evidence` artifact. This is package/simulation
evidence only; it does not claim camera, Jetson, TensorRT, ROS 2, broker, or
actuator compatibility.
