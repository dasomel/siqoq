# Issue #54 replay: siqoq-sim-to-edge-workflow (2026-10-04)

Fresh Claude Code subagent session (claude-sonnet-5-5), clean worktree of origin/main
(`chore/54-skill-verification-evidence`). Started from `AGENTS.md` / `CLAUDE.md` only.
Toolchain: `uv venv --python /opt/homebrew/bin/python3.12 .venv` inside the worktree
(`.venv/` is git-ignored), `uv pip install -e '.[dev]' build` (ruff 0.16.10, pytest 9.1.1).
Base install only; `[vision,transport,observability]` extras were not installed.

## Step 1 activation

`.agents/skills/` contains one skill. Frontmatter description (only text read before activating):
"Implement Siqoq's simulation-first perception pipeline while preserving compatible
virtual/physical sensor interfaces, portable inference, semantic-event boundaries, observability,
and safe actuator isolation. Use for recorded/webcam/simulated sensors, vision inference, event
schemas/bus, edge-runtime portability, or early physical-AI integration work."

Representative task chosen from the description: "Add a recorded-fixture camera source and route
its detections through a semantic event to the policy/action boundary." The description matches
(recorded sensors, semantic events, safe actuator isolation), so the skill activates. `AGENTS.md`
also names the skill explicitly for sensor/inference/event/edge-portability changes. Then read the
skill; its frontmatter is `metadata.openforge-version: "1"`, maturity `verified`.

## Step 2 happy path (scratch only)

Followed the skill workflow steps 1-9 on the existing code (analysis, no source edits):
`AGENTS.md`, `docs/principles.md` (principles 3, 4, 6), then `src/siqoq/policy.py` and
`src/siqoq/actuation.py`.

Commands and real output (outputs written to a scratch dir outside the repo):

- `siqoq demo` -> exit 0:
  `{"type":"object.detected","source":"sim.camera.front","object":"person","confidence":0.94,...,"schema_version":1}`
- `siqoq scenario run --config <scratch>/sc.json` (copy of `examples/scenario.json`, only
  `output_path` redirected) -> exit 0:
  `{"action_counts": {"log_detection": 3}, ..., "event_count": 3, "sequence_hash": "25f893c180473bf3e429a034687ba64cafa19aca921162b4472c6012d37a2611", "type_counts": {"object.detected": 3}}`
  Output file held 3 `object.detected` events with source `recorded.camera.front`.
- Python one-liner, event -> `decide()` -> `decide_and_execute(MockActuatorAdapter())` -> exit 0:
  `MockAction(action='log_detection', event_type='object.detected', mock=True)` then
  `ActionResult(... outcome='executed' ...)`.

Observation: the recorded fixture and the generated sensor both feed the same event ->
policy -> mock-actuator path; the source type does not appear in downstream logic (skill step 2/4/7).
Nothing in the repo was modified; `git status --short` was empty after this step.

## Step 3 failure/edge case (real project-specific hazard)

Hazard: skill step 7 / principle 6 / `policy.py` D1 and `MockAction` docstring: the `mock` field
is "REVIEWED and pinned to True"; flipping the default silently is a design change needing safety
sign-off.

Mutation: `sed -i '' 's/    mock: bool = True/    mock: bool = False/' src/siqoq/policy.py`
(one-line diff, confirmed with `git diff --stat`).

- `pytest -q` on the mutated tree -> exit 1. Failures:
  - `tests/test_actuation.py::test_decide_and_execute_propagates_correlation_id`
  - `tests/test_policy.py::test_action_contract_version_is_declared_and_mock_is_reviewed`
  - `tests/test_policy.py::test_decide_is_deterministic_and_mock_only`
  (the actuation test fails because the adapter returns `rejected` instead of `executed`.)
- Revert: `git checkout src/siqoq/policy.py`; `git status --short` empty.
- `pytest -q` after revert -> exit 0.

The repository's own pre-existing tests catch the violation deterministically. I did not mutate
the second guard (`policy.py` importing `actuation`, covered by
`tests/test_actuation.py::test_policy_module_never_imports_actuation`); it was not exercised
live.

## Step 4 repository verification

`make verify` (venv activated; AGENTS.md and skill step 8 name it as the canonical baseline) -> exit 0:

- `ruff check .` -> `All checks passed!`
- `pytest` -> `160 passed, 4 skipped in 3.44s`
- `python -m build` -> `Successfully built siqoq-0.1.0.dev0.tar.gz and siqoq-0.1.0.dev0-py3-none-any.whl`

Also standalone `ruff check .` -> exit 0 after the revert.

## Step 6 audit

Before the evidence JSON existed:
`python3 .../openforge/templates/scripts/audit-agent-skills.py . --strict` -> exit 1,
`ERROR SKILL-VERIFICATION-EVIDENCE ... verified skill requires .agents/skill-evals/siqoq-sim-to-edge-workflow.json`.
The post-write result is stated in the final message of the replay session, not here.

## Not verified

- Optional-extra adapters: `UsbWebcamFrameSensor` (no webcam), `OnnxCvInferenceAdapter`
  (extras not installed), NATS/MQTT transport (no broker). `make verify-full` was not run.
  4 tests were skipped by pytest in the base install; skip reasons were not inspected.
- Jetson/ARM, TensorRT, ROS 2, Kubernetes/K3s, container build (`make container*`, no docker
  run), real GPIO/actuator behaviour. Only mock adapters were exercised.
- `siqoq` CLI was run only on the macOS host, not on a second architecture.
- Skill steps 5 (observability context) and 6 (cloud routing separation) were read against the
  code but not exercised by a dedicated check in this replay.
