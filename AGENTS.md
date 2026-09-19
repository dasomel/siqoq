# Siqoq Agent Contract

Siqoq follows the OpenForge context-efficient agent engineering model. It is still in early bootstrap / architecture validation, so preserve explicit interfaces and avoid prematurely hardening one hardware/vendor path into the platform.

Inspect only the repository guidance, architecture/development document, matching project skill under `.agents/skills/`, and issue/spec that are relevant to the current task.


## Instruction routing

- `AGENTS.md` is the canonical portable repository contract.
- Load detailed documents and `.agents/skills/` only when they are relevant to the current task; do not preload them by default.
- Tool-specific adapters must contain only runtime-specific behavior and must not duplicate this contract.
- Deterministic requirements belong in scripts, tests, linters, policy, or CI when they can be enforced reliably.

For simulation/recorded/physical sensor interfaces, vision inference, semantic events/event bus, edge-runtime portability, or physical-AI pipeline changes, load `.agents/skills/siqoq-sim-to-edge-workflow/SKILL.md`.

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

## Risk-scaled change workflow

- Class A documentation-only changes use the Issue/PR as the change record.
- Class B internal behavior changes require explicit acceptance criteria; use a Change Package when the work is complex, cross-component, or operationally risky.
- Class C dependency/runtime/toolchain/build-contract changes and Class D release/deployment/security-boundary changes require an accepted Change Package before broad implementation.
- For Class C/D or complex Class B work, load `.agents/skills/change-package-workflow/SKILL.md` and use `templates/change/CHANGE.md` plus `templates/change/TASKS.md` when a versioned working artifact is useful.
- Keep requirement → acceptance scenario → task → evidence traceability. Material scope changes require package update and re-review.
- At completion, synchronize durable truth into code/tests, normative docs, ADRs, evidence, and portfolio/status records; do not maintain a duplicate long-lived specification tree.

## Verification

`make verify` is the canonical local baseline and mirrors CI: Ruff, pytest, and package build.

A green Python gate does not prove camera/device, ONNX/TensorRT, NATS/MQTT, ROS 2, Kubernetes/K3s, or real actuator behavior. State which simulation/edge/hardware path was actually exercised before claiming those properties.

## Convergence

End substantive work as A) complete/verified, B) meaningful verified progress with the next blocker isolated, or C) stop with evidence when further work requires unjustified scope, premature hardware coupling, unsafe physical side effects, unsupported assumptions, or unacceptable risk.

Reference: https://github.com/dasomel/openforge/blob/main/docs/agent-engineering.md
Agent Skills standard: https://github.com/dasomel/openforge/blob/main/docs/agent-skills.md
