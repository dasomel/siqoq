# Siqoq Contract Specifications

**English** | [한국어](README.ko.md)

Siqoq should remain small at the implementation core and explicit at its boundaries. This directory will hold the stable, versioned contracts that let simulation, laptops, edge devices, and physical systems interoperate.

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
- event type and source
- confidence and model provenance
- correlation/trace identifiers
- timestamps
- optional references to large/raw artifacts rather than embedding them by default

### Action Contract

Defines requests and results crossing from reasoning/policy into potential physical execution.

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

### Capability Contract

Describes what an edge node, simulator, or adapter can provide without exposing vendor-specific APIs to the core scheduler/runtime.

## Versioning principles

- contracts are versioned independently of implementation packages where useful
- additive compatible changes are preferred
- vendor SDK types do not appear in core schemas
- large binary sensor payloads should normally be referenced, not embedded in semantic events
- safety-sensitive action fields require explicit compatibility review
- simulator and physical implementations should share conformance tests

## Conformance philosophy

An adapter is not considered supported merely because it compiles. A supported adapter should pass a shared conformance suite for its contract.

Examples:

```text
RecordedVideoAdapter ─┐
WebcamAdapter ────────┼─→ Sensor Contract Conformance
IsaacSimAdapter ──────┤
ROS2CameraAdapter ────┘
```

This is the basis for Siqoq's simulation-to-reality portability goal.
