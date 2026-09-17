# sim-to-edge Agent Skill fresh-session verification (issue #36)

Date: 2026-09-17. Fresh Claude session, no memory of prior work, following
`.agents/skills/siqoq-sim-to-edge-workflow/SKILL.md`'s own numbered workflow.

Relation to `docs/evaluations/sim-to-edge-replay.md`: that file already recorded a
`make verify`/`siqoq scenario run` pass and claimed "verified" status, but the
skill frontmatter was still `draft` and that report did not exercise the
required failure/edge-case regression (missing fixture, malformed record) as a
live command in this session. This report supersedes it as the basis for the
maturity decision by independently re-running the happy path and adding the
edge-case evidence issue #36 requires.

## Activation correctness

Read `AGENTS.md`, `docs/architecture.md`, `docs/principles.md`, and the
SKILL.md itself. Skill's "Use When" correctly scopes to
sensor/inference/event/edge-portability work; "Do Not Use When" correctly
excludes fleet/GitOps and direct actuation. Matches the repo's own
architecture boundaries.

## Happy path (simulation pipeline evidence)

Built a Python 3.12 venv (ambient python3 was 3.10) at `/tmp/verify-venv36`
with `pip install -e '.[dev,vision,transport,observability]'`.

- `siqoq demo`:
  `{"type":"object.detected","source":"sim.camera.front","object":"person","confidence":0.94,...}`
  — generated-sensor path works end to end (sensor -> inference -> semantic event).
- `siqoq scenario run --config examples/scenario.json`:
  `{"event_count": 3, "sequence_hash": "25f893c18...", "type_counts": {"object.detected": 3}}`,
  and `scenario-events.jsonl` contains 3 well-formed semantic events from the
  recorded fixture `tests/fixtures/recorded_detections.jsonl` — fixture/recorded
  sensor path -> inference -> event -> JSONL transport output confirmed by
  reading the actual output file, not just the summary line.

Read `sensors.py`, `events.py`, `transport.py`, `scenario.py`: `SensorAdapter`
protocol is source-agnostic; `FixtureSensorAdapter` parses JSONL and validates
each record via `SensorSample.from_record`; `scenario.py` wires
adapter -> event -> transport writer. Code genuinely implements the claimed path.

## Failure/edge-case regression (required by issue #36)

Ran two live failure cases, not just cited existing unit tests:

1. Missing fixture file (`tests/fixtures/does-not-exist.jsonl`): `siqoq scenario
   run` exits 1 with `FileNotFoundError: [Errno 2] No such file or directory`
   raised from `sensors.py:93` before any event is emitted; output file created
   empty (0 bytes).
2. Malformed record (`confidence: 9`, out of `[0,1]`): exits 1 with
   `ValueError: line 1: confidence must be a number between 0 and 1` from
   `SensorSample.from_record`; output file empty.

Both confirm the required property: missing/unavailable input surfaces a
measurable failure, not fabricated semantic output.

## Actuator safety boundary

Read `src/siqoq/policy.py` in full. `_ACTION_BY_TYPE` maps only to
`"log_detection"` / `"noop"`; `SafetyGate.approve` is a pure boolean gate; no
import, client, or call to any real actuator, network device, or GPIO exists
anywhere in the module (confirmed by reading the whole file, not grepping a
keyword). Comment `D1` explicitly documents mock-only-by-construction design
intent. No actuation code path exists to audit further.

## `make verify` (package/lint/unit evidence)

Fresh run from the venv above:

```
ruff check .        -> All checks passed!
pytest               -> 41 passed, 3 skipped in 7.55s
python -m build      -> Successfully built siqoq-0.1.0.dev0.tar.gz and siqoq-0.1.0.dev0-py3-none-any.whl
```

## Evidence separation (required by issue #36)

- (a) Python package/lint/unit: `ruff check .` clean, `pytest` 41 passed/3
  skipped, `python -m build` succeeded. This proves the Python package is
  correct and buildable — nothing more.
- (b) Simulation pipeline: `siqoq demo` and `siqoq scenario run` both produce
  real semantic events end-to-end on the laptop path (generated and
  fixture/recorded sensors), and the required failure/edge case was
  reproduced live in this session.
- (c) Physical/edge hardware: NONE exists and NONE was exercised. No camera
  capture, no Jetson/ARM deployment, no ONNX/TensorRT runtime, no ROS 2, no
  real NATS/MQTT broker, and no real actuator are implemented or tested
  anywhere in this repo at this commit. `verified` maturity below applies only
  to the hardware-free simulation/laptop MVP path — it must not be read as a
  claim about any of the above.

## Verdict

All issue #36 acceptance criteria are satisfied with fresh evidence gathered
in this session: correct activation, happy path (both sensor sources), the
required failure/edge-case regression, `make verify`, and explicit evidence
separation. Skill maturity promoted `draft` -> `verified` for the sim/laptop
MVP path only.
