# Simulation Adapter Contract v0

Status: v0 (draft, matches `CONTRACT_VERSION = 0` in `siqoq.sensors`).

This spec formalizes what makes a `SensorAdapter` (Sensor Contract v0,
`docs/specs/sensor-contract.md`) "simulated" rather than "real/recorded" or
"physical". It is **not** a new protocol: a simulation adapter is a
`SensorAdapter` specialization, distinguished by provenance and by extra
determinism guarantees a CI-safe simulated source must uphold — not by a
different method signature.

## What makes a source "simulated"

A `SensorAdapter` implementation is a *simulation adapter* when:

- it produces `SemanticEvent`s synthetically (generated, scripted, or driven
  by a simulator) rather than sourcing them from a physical sensor or a
  recording of one;
- it tags its output `metadata["provenance"] = PROVENANCE_SIMULATED`
  (`siqoq.events`), per the Semantic Event Contract v0 provenance
  convention (`docs/specs/semantic-event-contract.md`).

This is distinct from:

- **recorded** (`PROVENANCE_RECORDED`): replays previously captured data
  (e.g. `FixtureSensorAdapter` reading a JSONL fixture). Recorded sources
  are deterministic by construction (the file content is fixed) but are not
  "simulated" — nothing is being synthesized.
- **physical** (`PROVENANCE_PHYSICAL`): reads a live physical sensor. Never
  deterministic, never CI-safe as a source of truth for assertions.

`GeneratedSensorAdapter` is the reference simulation adapter implementation:
it satisfies `SensorAdapter` and is exercised by the same conformance suite
as `FixtureSensorAdapter` (`tests/test_sensors.py`), because both are, at
the contract level, ordinary `SensorAdapter`s.

## Determinism requirements for CI-safe simulated adapters

A simulation adapter that CI relies on for regression assertions MUST be
deterministic: **same inputs -> same outputs**, byte-for-byte, across runs
and across machines. Concretely:

- No wall-clock leakage into any value that is hashed or compared in a test
  or scenario summary. This is the same pattern already enforced in
  `siqoq.scenario`: `ScenarioSummary.duration_seconds` is wall-clock and
  explicitly excluded from `sequence_hash` (`_sequence_hash` hashes only
  event payloads, never timing), and it is documented as a "coarse CI
  sanity signal only, not a benchmark measurement" that tests must never
  assert a tight bound on. A simulation adapter must not introduce a new
  wall-clock-derived value (e.g. `datetime.now()`) into any field that ends
  up hashed, JSON-compared, or asserted equal across runs.
- Any time-varying field a simulation adapter emits (e.g. `timestamp`) MUST
  be fully determined by an explicit, caller-supplied parameter rather than
  ambient clock state, whenever the adapter is used in a context that
  requires reproducible output (tests, scenario benchmarks). Non-deterministic
  convenience defaults (e.g. "use the current time if unset") are permitted
  only when the caller has not opted into a fixed value, and must not be
  relied upon for any CI assertion.
- Given the same construction parameters and the same `read(count=N)` call,
  two independent runs MUST yield an identical `SemanticEvent` sequence
  (identical `to_json()` output, in order).

`GeneratedSensorAdapter` satisfies this today via its `timestamp: str | None`
field: when a caller passes a fixed `timestamp`, every event yielded by
`read()` carries that exact value instead of ambient clock time, making the
adapter's output byte-for-byte reproducible across runs. This is verified by
`tests/test_sensors.py::test_adapter_is_deterministic_with_fixed_timestamp`
and `test_generated_adapter_is_deterministic_and_simulated_provenance_ready`.

## Simulator SDK isolation

Future simulator bridges (e.g. Isaac Sim, Gazebo) MUST NOT leak
simulator-specific SDK types into `SensorAdapter` or `SemanticEvent`
signatures. A bridge adapter's `read()` method returns plain
`SemanticEvent` instances built from normalized Python primitives (`str`,
`float`, `dict`), exactly like `GeneratedSensorAdapter` and
`FixtureSensorAdapter` do today. Any simulator SDK object (a scene handle, a
sensor proxy, a physics-engine type) is confined to the adapter's
implementation internals and must never appear as a parameter type, return
type, or field type on `SensorAdapter`/`SemanticEvent`. This mirrors the
existing frame-level rule in `docs/specs/sensor-contract.md` ("No vendor SDK
type ... appears in this contract").

## Compatibility rules

Same as Sensor Contract v0 (`docs/specs/sensor-contract.md#compatibility-rules`):
this spec adds guarantees on top of the existing `SensorAdapter` protocol
and does not modify its method signature, so it does not require a
`CONTRACT_VERSION` bump. A future change that weakens the determinism
guarantee above (e.g. permitting ambient clock leakage into hashed output
by default) would be breaking.

## Conformance

- `tests/test_sensors.py` exercises `GeneratedSensorAdapter` under the
  shared `SensorAdapter` conformance suite (Sensor Contract v0) and under a
  dedicated determinism/provenance-readiness test for this spec.
- `siqoq.scenario._sequence_hash` is the canonical example of computing a
  CI-safe, wall-clock-free hash over adapter output.
