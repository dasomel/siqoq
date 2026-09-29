# Research Notes

This document records time-sensitive external references used to shape Siqoq's roadmap. It should be updated when the ecosystem materially changes.

## 2026-08 review

### Microsoft Physical AI Toolchain

- Repository: https://github.com/microsoft/physical-ai-toolchain
- Notable pattern: graduated T0–T5 adoption model
- T0 starts locally without cloud/Kubernetes; higher tiers add storage, training, k3s/GitOps, fleet delivery, and fleet intelligence
- Relevance to Siqoq: define explicit graduation criteria rather than enabling every platform feature from day one

### Open Edge Platform Physical AI Studio

- Repository: https://github.com/open-edge-platform/physical-ai-studio
- Notable pattern: end-to-end imitation-learning application with CLI/API/GUI and multiple export backends
- Relevance to Siqoq: keep inference/export adapters flexible and build benchmarkable user-facing scenarios without becoming another training framework

### Hugging Face LeRobot

- Repository: https://github.com/huggingface/lerobot
- Notable patterns: standardized datasets, hardware-agnostic robot interfaces, simulation evaluation, policy plugin model, unified rollout/deployment CLI
- Security lesson: remote policy/model artifacts and remote code need explicit trust and revision/pinning rules when software can control physical hardware

### OpenRAL

- Repository: https://github.com/OpenRAL/openral
- Notable pattern: typed contracts across hardware/sensors/world state/skills/reasoning/safety/observability
- Relevance to Siqoq: strengthen contract versioning, conformance testing, safety, and traceability while avoiding overlap with full robot-agent runtime scope

### Physical AI Harness

- Repository: https://github.com/nanxintin/physical-ai-harness
- Notable pattern: unified simulated/real device access and MCP-facing agent tools
- Relevance to Siqoq: consider MCP as an optional adapter, never as a required control path; retain a separate safety/action boundary

## Research policy

- Prefer primary project repositories and official documentation.
- Record the observation date when a decision depends on rapidly changing features.
- Do not copy another project's architecture wholesale; extract patterns that reinforce Siqoq's own scope.
- Re-evaluate competitive overlap before implementing a large new subsystem.
