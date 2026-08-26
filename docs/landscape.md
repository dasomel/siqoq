# Physical AI OSS Landscape

**English** | [한국어](landscape.ko.md)

This document records projects Siqoq should learn from, integrate with, or deliberately avoid duplicating. It is not a ranking. The purpose is to keep Siqoq's scope clear as the Physical AI ecosystem evolves.

## Positioning summary

Siqoq is **not** trying to become another full robotics training platform, agent runtime, simulator, or cloud control plane.

Its intended focus is:

> **Portable simulation-to-edge contracts and runtime infrastructure for Physical AI experimentation, with semantic events, observability, and an explicit safety boundary before physical action.**

## Microsoft Physical AI Toolchain

Reference: https://github.com/microsoft/physical-ai-toolchain

What it already does well:

- laptop-first T0 development path
- graduated T0–T5 adoption model
- Jetson edge capture and inference
- Isaac Sim / Isaac Lab integration
- LeRobot-based training/evaluation
- ONNX/TensorRT deployment
- k3s/GitOps and multi-site fleet progression
- cloud training and enterprise Azure integration

What Siqoq should learn:

- use clear maturity tiers instead of an all-or-nothing stack
- define graduation triggers between laptop, lab, edge, and fleet modes
- keep Kubernetes/cloud optional until scale justifies them

What Siqoq should not duplicate:

- Azure infrastructure provisioning
- full training lifecycle orchestration
- enterprise cloud/federation control plane

## Open Edge Platform — Physical AI Studio

Reference: https://github.com/open-edge-platform/physical-ai-studio

What it already does well:

- end-to-end imitation-learning workflow
- VLA/policy training
- GUI, Python API, and CLI
- OpenVINO/ONNX/Torch export
- benchmark-oriented evaluation

What Siqoq should learn:

- provide a simple local entry point and eventually a visual workflow
- define reproducible demo scenarios and benchmarks
- keep inference backends pluggable

What Siqoq should not duplicate:

- policy training framework
- VLA model zoo
- robot-learning application UI as the core product

## Hugging Face LeRobot

Reference: https://github.com/huggingface/lerobot

What it already does well:

- standardized robot datasets
- teleoperate → record → train → deploy workflow
- broad robot/policy ecosystem
- simulation evaluation
- unified real-robot policy deployment CLI
- plugin model for third-party policies

What Siqoq should learn/integrate:

- treat LeRobot datasets and policies as an optional upstream/downstream integration
- reuse existing policy deployment where appropriate instead of inventing another model ecosystem
- consider out-of-tree adapter/plugin patterns
- adopt strong security rules for remotely downloaded model/policy artifacts

What Siqoq should not duplicate:

- dataset format and Hub ecosystem
- robot policy library
- imitation/RL/VLA training stack

## OpenRAL

Reference: https://github.com/OpenRAL/openral

OpenRAL describes itself as a typed, traceable, safety-first Robot Agentic Layer with explicit boundaries across hardware, sensors, world state, skills, reasoning, safety, and observability.

What Siqoq should learn:

- strongly typed/versioned contracts at boundaries
- make safety and observability architectural layers rather than add-ons
- distinguish fast control/policies from slower reasoning paths

Potential overlap:

- perception/world-state/action contracts
- safety and observability
- runtime abstraction

Siqoq differentiation:

- remain focused on **simulation-to-edge portability and infrastructure**, not a complete robot-agent runtime
- agent reasoning stays optional
- semantic event transport and edge/fleet operations remain first-class concerns

## Physical AI Harness

Reference: https://github.com/nanxintin/physical-ai-harness

What it does:

- exposes simulated and real devices through standardized interfaces
- enables LLM agents to interact with physical devices
- uses MCP as a key agent/device interface

What Siqoq should learn:

- simulator/real-device parity is valuable
- an optional MCP adapter may be useful for agent integration

What Siqoq should avoid:

- making MCP or an LLM agent mandatory for the core runtime
- coupling physical device control directly to agent tool invocation without a Siqoq safety/action boundary

## NVIDIA Isaac Sim / Isaac Lab / OSMO

Siqoq should treat NVIDIA's simulation/training/orchestration stack as integrations, not dependencies that define the core architecture.

Potential integrations:

- Isaac Sim virtual sensor adapter
- deterministic simulation scenarios
- Isaac Lab/LeRobot outputs as optional policy artifacts
- TensorRT edge inference profile

The core Sensor/Event/Action contracts must remain usable without NVIDIA software.

## ROS 2

ROS 2 remains the standard integration point for many sensors, robots, navigation stacks, and hardware interfaces.

Siqoq's position:

- ROS 2 bridge/adapters: yes
- requiring ROS 2 for laptop MVP: no
- replacing ROS 2: no
- allowing core domain/event contracts to become ROS-message-specific: no

## Architectural gap Siqoq targets

The ecosystem already has strong solutions for:

- simulation
- robot learning/training
- datasets/model sharing
- ROS hardware integration
- agent runtimes
- hyperscale/cloud operations

Siqoq explores the smaller connective layer:

```text
cheap local experiment
      ↓
simulator / virtual sensor
      ↓
stable sensor contract
      ↓
portable perception runtime
      ↓
semantic event
      ↓
observable decision/action boundary
      ↓
edge target
      ↓
optional robot/fleet integration
```

The project should stay useful before a user owns a robot, before they select a cloud, and before they select an agent framework.

## Reuse-before-build rule

Before implementing a new subsystem, ask:

1. Is there already a mature OSS project that owns this problem?
2. Can Siqoq integrate it through an adapter instead?
3. Is the proposed feature part of Siqoq's simulation-to-edge contract/runtime mission?
4. Can it remain optional for the laptop-first path?
5. Can it be tested without the target hardware?

If the first two answers are yes and the third is no, prefer integration over reimplementation.
