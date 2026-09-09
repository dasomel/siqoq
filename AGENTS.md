# Siqoq Agent Contract

Siqoq follows the OpenForge context-efficient agent engineering model. It is still in early bootstrap / architecture validation, so preserve explicit interfaces and avoid prematurely hardening one hardware/vendor path into the platform.

Read `README.md`, `docs/architecture.md`, `docs/principles.md`, `docs/development.md`, the matching project skill under `.agents/skills/`, and the relevant issue/spec before editing.

## Product and architecture boundaries

- Simulation first: software paths must be developable without physical hardware on day one.
- Hardware is optional and replaceable. Jetson is an important target, not the platform definition.
- Preserve compatible sensor interfaces between simulated/recorded and physical sources.
- Keep portable inference/workload logic separate from hardware-specific acceleration adapters.
- Prefer semantic events as the boundary after edge inference instead of coupling downstream policy/agents directly to raw media streams.
- Keep actuation behind an explicit adapter/policy boundary. Treat any new physical side effect or actuator authority as a high-risk design change.
- Preserve observability across input -> inference -> semantic event -> decision -> action when those stages exist.
- Do not introduce fleet/GitOps complexity before the single-node/software-first path needs it.

## Engineering rules

- Make the smallest coherent change that solves the requested problem.
- Do not auto-fix unrelated findings; report them separately.
- Treat sensor/event schema changes, public APIs, hardware-specific dependencies, cloud/model routing, actuator behavior, filesystem/network authority, and destructive device operations as design changes.
- Keep virtual and physical adapters behind stable interfaces rather than branching application logic throughout the codebase.
- Let formatter/linter/test tooling own deterministic style. Comments explain why, invariants, hazards, or hardware/runtime compatibility constraints.
- For bugs, prefer: reproduce -> failing test/evidence -> minimal fix -> same test passes -> relevant regression suite.

## Verification

`make verify` is the canonical local baseline and mirrors CI: Ruff, pytest, and package build.

A green Python gate does not prove camera/device, ONNX/TensorRT, NATS/MQTT, ROS 2, Kubernetes/K3s, or real actuator behavior. State which simulation/edge/hardware path was actually exercised before claiming those properties.

## Convergence

End substantive work as A) complete/verified, B) meaningful verified progress with the next blocker isolated, or C) stop with evidence when further work requires unjustified scope, premature hardware coupling, unsafe physical side effects, unsupported assumptions, or unacceptable risk.

Reference: https://github.com/dasomel/openforge/blob/main/docs/agent-engineering.md
Agent Skills standard: https://github.com/dasomel/openforge/blob/main/docs/agent-skills.md
