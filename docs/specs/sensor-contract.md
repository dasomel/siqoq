# Sensor Contract v0

Status: v0 (draft, matches `CONTRACT_VERSION = 0` in `siqoq.sensors` and
`siqoq.video_sensors`).

Siqoq has two sensor contract layers. They are not competing abstractions;
each solves a different boundary and one is usually composed on top of the
other.

## Layer 1: event-level (`siqoq.sensors.SensorAdapter`)

```python
class SensorAdapter(Protocol):
    def read(self, *, count: int) -> Iterator[SemanticEvent]: ...
```

Guarantees (v0):

- `read(count=N)` yields at most `N` `SemanticEvent` instances, in order.
- Every yielded event satisfies the Semantic Event Contract v0
  (`docs/specs/semantic-event-contract.md`): `type`, `source`, `object`,
  `confidence`, `timestamp`, `schema_version` are present, `confidence` is a
  `float` in `[0, 1]`, `source`/`object`/`timestamp` are non-empty strings.
- Adapters MUST NOT raise on well-formed input; malformed fixture input
  raises `ValueError` naming the offending line (see
  `FixtureSensorAdapter`).
- Both `GeneratedSensorAdapter` (synthetic/simulated) and
  `FixtureSensorAdapter` (recorded) implement this contract identically and
  are exercised by the same conformance suite (`tests/test_sensors.py`).

## Layer 2: frame-level (`siqoq.video_sensors.FrameSensor`)

```python
class FrameSensor(Protocol):
    def open(self) -> None: ...
    def read(self) -> Frame | None: ...
    def close(self) -> None: ...
```

Guarantees (v0):

- Explicit lifecycle: `open()` before `read()`; `read()` returns `None` on
  exhaustion instead of raising; `close()` is idempotent-safe to call after
  exhaustion.
- `Frame` = normalized `FrameMetadata` (source, index, timestamp, width,
  height, format) + raw `payload: bytes`. No vendor SDK type (e.g. an OpenCV
  `Mat`, a codec-specific frame object) appears in this contract.
- `FrameSensor` implementations (`RecordedVideoFileSensor`,
  `MockWebcamFrameSensor`, `UsbWebcamFrameSensor`) are a lower layer than
  `SensorAdapter`: a frame producer is typically paired with an
  `InferenceAdapter` (`siqoq.inference`) to turn frames into the
  `SemanticEvent`s that a `SensorAdapter` yields. Siqoq does not currently
  ship a `FrameSensor + InferenceAdapter -> SensorAdapter` bridge; adding one
  is a straightforward, non-breaking follow-up.

## Relationship between the two layers

```text
FrameSensor (frame-level)  --InferenceAdapter-->  SemanticEvent  <--yielded by--  SensorAdapter (event-level)
```

`SensorAdapter` is the stable, higher-level contract most policy/transport
code should depend on. `FrameSensor` exists because some sources (recorded
video, webcams) naturally produce frames, not pre-classified events; keeping
it separate lets inference remain swappable (mock vs. ONNX/OpenCV) without
touching the event-level contract.

## Compatibility rules

- **Breaking** (requires `CONTRACT_VERSION` bump): removing/renaming a
  protocol method, changing `read()`'s return semantics (e.g. making it
  raise on exhaustion instead of returning `None`/stopping iteration),
  removing a required `FrameMetadata`/`Frame` field, or narrowing the set of
  values a required field may take.
- **Additive/compatible** (no bump required): a new optional
  keyword-only parameter with a default, a new optional field on
  `FrameMetadata`, a new `SensorAdapter`/`FrameSensor` implementation, or
  documentation-only clarifications.

## Conformance

`tests/test_sensors.py` parametrizes the shared conformance suite over
`GeneratedSensorAdapter` (fake/simulated) and `FixtureSensorAdapter`
(real/recorded fixture data), asserting both the general adapter behavior
and the Sensor Contract v0 field/shape guarantees above.

## Pipeline-level compatibility (Phase 2)

The adapter-level conformance suite above proves `GeneratedSensorAdapter`
and `FixtureSensorAdapter` satisfy the same `SensorAdapter` protocol. That is
necessary but not sufficient for Phase 2's acceptance criterion that "the
same downstream pipeline consumes simulated and real camera inputs" — it
does not by itself show the *pipeline* (`siqoq.scenario.run_scenario`)
avoids branching on which adapter it was given.

`tests/test_scenario.py::test_build_adapter_is_the_only_dispatch_point_on_adapter_type`
inspects `run_scenario`'s source to assert `ScenarioConfig.build_adapter()`
is the only place that branches on `adapter`/source type; `run_scenario`
itself calls `adapter.read()` exactly once, through the shared protocol.
`tests/test_scenario.py::test_run_scenario_pipeline_shape_matches_across_generated_and_fixture_sources`
runs the identical `run_scenario()` call against a `ScenarioConfig(adapter="generated", ...)`
and a `ScenarioConfig(adapter="fixture", source_path=..., ...)` and asserts
both produce `ScenarioSummary` objects with the same field set and shape
(`event_count`, `type_counts` keys, `action_counts` keys). Together these
satisfy Phase 2's acceptance criterion end-to-end, not just at the adapter
boundary.
