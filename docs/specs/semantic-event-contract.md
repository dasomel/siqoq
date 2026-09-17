# Semantic Event Contract v0

Status: v0 (`SCHEMA_VERSION = 1` in `siqoq.events`; the contract itself is
versioned as "v0" while its wire schema version integer is `1` — see
"Versioning note" below).

`SemanticEvent` is the stable boundary between inference/sensor adapters and
downstream policy/transport code (see `docs/architecture.md`, "Semantic
event layer").

## Required fields

`REQUIRED_FIELDS = ("type", "source", "object", "confidence", "timestamp", "schema_version")`

- `type: str` — event kind, e.g. `"object.detected"`.
- `source: str` — producer identifier, e.g. `"sim.camera.front"`,
  `"file.video.recorded"`.
- `object: str` — the detected/observed entity.
- `confidence: float` — in `[0, 1]`.
- `timestamp: str` — ISO 8601.
- `schema_version: int` — the `SCHEMA_VERSION` this event was produced under.

## Optional fields

`OPTIONAL_FIELDS = ("correlation_id", "metadata")`

- `correlation_id: str | None` — for tracing one detection across pipeline
  stages.
- `metadata: dict[str, Any]` — free-form, vendor-agnostic extra context.
  `to_json()` omits both optional fields entirely when empty/`None`, so old
  consumers reading only required keys are unaffected by their presence.

## Provenance metadata (simulated vs. real/recorded)

New in this spec, additive-only: producers SHOULD set
`metadata["provenance"]` to one of the constants exported by
`siqoq.events`:

- `PROVENANCE_SIMULATED = "simulated"` — synthetic/generated data
  (`GeneratedSensorAdapter`).
- `PROVENANCE_RECORDED = "recorded"` — fixture/recorded data
  (`FixtureSensorAdapter`, `RecordedVideoFileSensor`).
- `PROVENANCE_PHYSICAL = "physical"` — a live physical sensor.

This is a *convention on the existing `metadata` dict*, not a new required
field: no `SCHEMA_VERSION` bump was needed. Consumers that need provenance
MUST tolerate its absence (older/non-conforming producers) rather than
treating it as required.

## Vendor neutrality

No OpenCV (`cv2`), ONNX Runtime (`onnxruntime`), NATS, or MQTT type appears
in `SemanticEvent`'s field types or `siqoq.events`'s public API — all fields
are Python primitives (`str`, `float`, `int`, `dict`). Adapters that wrap
vendor SDKs (e.g. `OnnxCvInferenceAdapter`) convert to this contract at their
boundary; the contract module itself never imports a vendor SDK.

## Compatibility rules

- **Breaking** (`SCHEMA_VERSION` bump required): removing or renaming a
  required field, changing a required field's type or valid value range,
  or changing `to_json()`'s key *meaning* (renaming a key is breaking even
  if the value shape is unchanged).
- **Compatible / additive** (no bump): adding a new optional field, adding a
  new `metadata` key convention (such as `provenance` above), adding a new
  `type` value, or relying on a differently-ordered but same-key JSON
  payload (`to_json()` never promises key order).

## Versioning note

The contract-level label ("v0") and the wire-level `SCHEMA_VERSION` integer
(`1`) are deliberately decoupled: `SCHEMA_VERSION` already existed pre-issue
#17 and is not renumbered here to avoid an unnecessary breaking-looking
diff. Future contract revisions bump `SCHEMA_VERSION` per the rules above;
the spec document version label tracks the same increments.
