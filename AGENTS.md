# Siqoq Agent Contract

Siqoq is in early bootstrap / architecture validation: preserve explicit interfaces and avoid prematurely hardening one hardware/vendor path into the platform. Change management and agent engineering follow the OpenForge model (https://github.com/dasomel/openforge/blob/main/docs/change-management.md, https://github.com/dasomel/openforge/blob/main/docs/agent-engineering.md); Class C/D changes use `templates/change/CHANGE.md` + `TASKS.md`.

For simulation/recorded/physical sensor interfaces, vision inference, semantic events/event bus, edge-runtime portability, or physical-AI pipeline changes, load `.agents/skills/siqoq-sim-to-edge-workflow/SKILL.md`.

## Product and architecture boundaries

- Simulation first: software paths must be developable without physical hardware on day one.
- Hardware is optional and replaceable. Jetson is an important target, not the platform definition.
- Preserve compatible sensor interfaces between simulated/recorded and physical sources; keep virtual and physical adapters behind stable interfaces rather than branching application logic.
- Keep portable inference/workload logic separate from hardware-specific acceleration adapters.
- Prefer semantic events as the boundary after edge inference instead of coupling downstream policy/agents directly to raw media streams.
- Keep actuation behind an explicit adapter/policy boundary. Treat any new physical side effect or actuator authority as a high-risk design change.
- Preserve observability across input -> inference -> semantic event -> decision -> action when those stages exist.
- Do not introduce fleet/GitOps complexity before the single-node/software-first path needs it.
- Treat sensor/event schema changes, public APIs, hardware-specific dependencies, cloud/model routing, actuator behavior, filesystem/network authority, and destructive device operations as design changes.

## Verification

`make verify` is the canonical local baseline and mirrors CI: Ruff, pytest, and package build.

A green Python gate does not prove camera/device, ONNX/TensorRT, NATS/MQTT, ROS 2, Kubernetes/K3s, or real actuator behavior. State which simulation/edge/hardware path was actually exercised before claiming those properties.
