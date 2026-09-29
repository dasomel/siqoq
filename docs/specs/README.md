# Siqoq Contract Specifications

**English** | [한국어](README.ko.md)

Siqoq should remain small at the implementation core and explicit at its boundaries. This directory holds the evolving contracts that let simulation, laptops, edge devices, and physical systems interoperate.

## Current implementation skeleton

The first code-level contract skeleton is now implemented in:

- `src/siqoq/contracts.py` — `SensorSample`, `Detection`, `ActionRequest`, `ActionResult`, `DeviceCapabilities`, and adapter protocols
- `src/siqoq/events.py` — versioned `SemanticEvent` envelope
- `src/siqoq/pipeline.py` — perception → event → policy → safety → action composition
- `src/siqoq/adapters.py` — generated sensor, static inference, in-memory transport, allow-list safety gate, and mock action adapter
- `src/siqoq/runtime.py` — runtime manifest and dependency-free capability discovery

These are intentionally minimal scaffolds, not frozen public APIs. Issue #17 will evolve them into explicit versioned specifications and a shared adapter conformance suite.

## Planned specifications

### Sensor Contract

Defines normalized sensor samples and lifecycle behavior independent of simulator/vendor APIs.

Initial scope:

- source identity and capability metadata
- timestamps and sequence numbers
- image/frame metadata without forcing one image transport
- health/readiness states
- simulated vs physical provenance
- optional calibration metadata

### Semantic Event Contract

Defines model-independent perception events such as detection, classification, tracking, anomaly, and state-change events.

Initial scope:

- versioned envelope
- event ID, type, and source
- confidence and model provenance
- correlation/trace identifiers
- timestamps and source sequence
- optional references to large/raw artifacts rather than embedding them by default

### Action Contract

Defines requests and results crossing from reasoning/policy into potential physical execution.

```text
Decision
  ↓
ActionRequest
  ↓
SafetyGate
  ↓
ActionAdapter
  ↓
Physical hardware
```

The current skeleton is safe-by-default: `NoOpPolicy` emits no actions, `AllowListSafetyGate` allows nothing unless explicitly configured, and `MockActionAdapter` never touches hardware.

Initial scope:

- action type and target
- requested parameters
- constraints and expiration
- policy/safety decision
- execution status/result
- correlation and audit metadata

### Runtime Manifest

Defines a portable declaration for a Siqoq workload.

Potential fields:

- sensor requirements
- model/runtime requirements
- CPU/GPU/accelerator constraints
- transport configuration
- telemetry configuration
- action capabilities
- deployment profile

The current `RuntimeManifest` provides a laptop-profile bootstrap and can be inspected through `siqoq inspect`.

### Capability Contract

Describes what an edge node, simulator, or adapter can provide without exposing vendor-specific APIs to the core scheduler/runtime.

The dependency-free bootstrap currently detects host architecture and intentionally leaves accelerator/sensor/actuator discovery empty until adapter-specific probes are added.

## Versioning principles

- contracts are versioned independently of implementation packages where useful
- additive compatible changes are preferred
- vendor SDK types do not appear in core schemas
- large binary sensor payloads should normally be referenced, not embedded in semantic events
- safety-sensitive action fields require explicit compatibility review
- simulator and physical implementations should share conformance tests

## Conformance philosophy

An adapter is not considered supported merely because it compiles. A supported adapter should pass a shared conformance suite for its contract.

```text
RecordedVideoAdapter ─┐
WebcamAdapter ────────┼─→ Sensor Contract Conformance
IsaacSimAdapter ──────┤
ROS2CameraAdapter ────┘
```

This is the basis for Siqoq's simulation-to-reality portability goal.
