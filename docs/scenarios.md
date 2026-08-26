# Deterministic Scenarios

**English** | [한국어](scenarios.ko.md)

Siqoq uses lightweight deterministic fixtures before full simulator or hardware integration. These fixtures are not a replacement for recorded video, Isaac Sim, Gazebo, or real sensors. They are a fast regression layer for validating Siqoq's contracts and perception-action flow on every supported CI architecture.

## Current fixture format

The bootstrap format is UTF-8 JSONL. Each non-empty line represents one normalized `SensorSample`.

```json
{"source":"fixture.camera.front","kind":"image","timestamp":"2026-01-01T00:00:00+00:00","sequence":0,"payload":{"frame":"frame-000"},"metadata":{"origin":"fixture"}}
```

The fixture deliberately stores only small logical payloads. Binary image/video data will be handled by later recorded-media adapters and references rather than making semantic events or regression fixtures carry large blobs by default.

## Run the first scenario

```bash
siqoq scenario examples/scenarios/person-detection.jsonl --name person-detection
```

The command emits a machine-readable summary containing scenario name, processed sample count, semantic event count, action result count, rejected action count, and detected host architecture.

## Bootstrap flow

```text
JSONL SensorSample fixture
          ↓
JsonlFixtureSensor
          ↓
StaticInference
          ↓
SemanticEvent
          ↓
DetectionRulePolicy
          ↓
AllowListSafetyGate
          ↓
MockActionAdapter
          ↓
ScenarioSummary
```

This proves the same boundaries that later real integrations must use, while requiring no network, broker, camera, GPU, ROS 2, or robot.

## Conformance

`GeneratedSensor` and `JsonlFixtureSensor` are exercised through the same lightweight Sensor Contract conformance helper. This is the first executable step toward the fuller adapter conformance suite tracked in issue #17.

## CI role

The scenario command runs on Linux AMD64, Linux ARM64, macOS AMD64, and macOS ARM64. A failure therefore catches both logical regressions and basic cross-platform assumptions before hardware-specific jobs are introduced.

## Next steps

- recorded-video adapter with deterministic media fixtures
- real webcam adapter
- OpenCV + ONNX Runtime baseline
- versioned formal schemas
- scenario assertions and benchmark metadata
- optional JSONL event artifacts
- later simulator-heavy regression jobs outside the fast default gate
