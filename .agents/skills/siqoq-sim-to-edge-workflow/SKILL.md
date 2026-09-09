---
name: siqoq-sim-to-edge-workflow
description: Implement Siqoq's simulation-first perception pipeline while preserving compatible virtual/physical sensor interfaces, portable inference, semantic-event boundaries, observability, and safe actuator isolation. Use for recorded/webcam/simulated sensors, vision inference, event schemas/bus, edge-runtime portability, or early physical-AI integration work.
license: Apache-2.0
compatibility: Requires the Siqoq checkout and Python 3.12 project toolchain; hardware/edge evidence depends on the target device and adapters available.
metadata:
  openforge-scope: project
  openforge-owner: dasomel/siqoq
  openforge-maturity: draft
  openforge-version: "1"
---

# Siqoq Simulation-to-Edge Workflow

## Use When

- Implementing the initial video/webcam/simulated-camera -> inference -> semantic-event -> NATS/MQTT/API path.
- Adding a sensor or inference adapter that must later move from laptop/simulation to x86/ARM/Jetson.
- Changing semantic event or observability contracts across the perception path.

## Do Not Use When

- Adding fleet-scale/GitOps machinery before the single-node MVP requires it.
- Adding direct physical actuation without an explicit safety/policy design.

## Inputs

- Relevant architecture/principles/roadmap issue.
- Source type: recorded media, simulated sensor, or physical sensor.
- Inference runtime and target environment.
- Semantic event contract and downstream consumer.

## Workflow

1. Read `AGENTS.md`, `docs/architecture.md`, `docs/principles.md`, and the relevant issue/spec.
2. Define or reuse a sensor interface that does not encode whether the source is simulated or physical into downstream business logic.
3. Keep hardware/runtime-specific acceleration behind an adapter so the same workload contract can run on laptop/x86/ARM/Jetson where supported.
4. Convert raw sensor input to an explicit inference result and then to a semantic event contract before policy/agent consumers depend on it.
5. Add observable context at boundaries that matter for the MVP: input identity/timing, inference result/latency, event publication, and downstream decision when present.
6. Keep optional cloud/model routing outside the stable sensor/event contracts so local execution remains viable.
7. Do not connect an actuator directly to model output. Route physical side effects through an explicit action adapter/policy boundary and require separate design/evidence.
8. Run `make verify` for the CI-equivalent Python baseline.
9. Exercise the most realistic available path for the feature: recorded/simulated source first, then real sensor/edge device only when the task claims that compatibility.

## Verification

Separate package/lint/unit evidence from simulation pipeline evidence and physical device/edge evidence. Do not claim Jetson, ROS 2, TensorRT, Kubernetes, sensor, or actuator correctness merely because the Python package builds.

This skill remains `draft` until the MVP workflow is replayed from a fresh session with at least one successful simulated path and one recorded failure/edge regression.

## Stop / Escalate When

- A hardware-specific dependency would leak through the core sensor/event interface.
- A change introduces physical actuation without explicit authorization/safety semantics.
- The implementation jumps to fleet/robotics complexity before the MVP contract is validated.
- The requested target capability cannot be measured and would require inventing hardware/runtime support.

## References

- `AGENTS.md`
- `README.md`
- `docs/architecture.md`
- `docs/principles.md`
- `docs/roadmap.md`
- root `Makefile`
