# Siqoq Vision

**English** | [한국어](vision.ko.md)

## Why Siqoq exists

Siqoq started from a practical question: **how can we experiment with Physical AI without buying specialized hardware first?**

The initial path was intentionally modest:

```text
image/video input
    ↓
vision inference
    ↓
semantic event
    ↓
edge runtime
    ↓
optional physical action
```

The project direction then expanded through research into edge AI, Jetson-class devices, simulation, robotics runtimes, and existing Physical AI OSS. The resulting conclusion is that Siqoq should not be "a Jetson demo" or "another robot framework." It should provide a portable path from digital experimentation to physical execution.

## The core transition

The most important idea discovered during the early research was the **Digital ↔ Physical boundary**.

```text
Digital World
  simulation / recorded data / models / agents
                │
                │  stable contracts
                ▼
             SIQOQ
                │
                │  sensor / event / action adapters
                ▼
Physical World
  cameras / edge devices / actuators / robots
```

Physical AI is not only about inference. It is about repeatedly crossing this boundary while preserving meaning, observability, and safety.

## The closed loop

Siqoq treats Physical AI as a closed feedback loop rather than a one-way inference pipeline.

```text
Sense
  ↓
Perceive
  ↓
Understand / World State
  ↓
Decide
  ↓
Act
  ↓
Observe Result
  └──────────────→ feedback to Sense
```

This is why semantic events, correlation IDs, action results, and end-to-end tracing are first-class concerns. A system that can only say "the model detected something" is incomplete once the output can affect the physical world.

## Simulation first, hardware later

The project deliberately introduces reality in stages:

1. generated or recorded data
2. webcam / real sensor on a laptop
3. deterministic simulator
4. edge accelerator such as NVIDIA Jetson
5. depth/LiDAR/IMU
6. mock actuator
7. constrained physical actuation
8. mobile robot or richer physical system

The purpose is not to delay hardware forever. It is to **move hardware risk to the point where software contracts are already testable and observable**.

## Edge as the bridge, not the destination

Edge hardware is important because latency, privacy, connectivity, and physical control often require local execution. But Siqoq should not be defined by any one board or accelerator.

Jetson is therefore an important validation target, while the architecture remains portable across ARM/x86 and different accelerators. CPU-only execution stays useful as the reference path.

## Why not another robotics framework?

The research showed that existing ecosystems already solve large parts of the stack well:

- ROS 2: robot middleware and communication
- Isaac Sim / Gazebo: simulation
- LeRobot: datasets, policies, robot-learning workflows
- vendor runtimes: optimized accelerator execution
- Kubernetes/K3s: orchestration at scale

Siqoq should integrate them through contracts and adapters rather than replace them.

The project owns the **portable simulation-to-edge path**, semantic event boundary, conformance between virtual/real adapters, decision observability, and the safety boundary before physical action.

## Why not make cloud mandatory?

Physical AI often needs cloud infrastructure for training, storage, fleet management, and large models. But a useful development path should work locally first.

Siqoq therefore prefers:

```text
local first
  ↓
edge capable
  ↓
cloud optional
  ↓
fleet when needed
```

Kubernetes and GitOps belong to later operational maturity, not the minimum developer experience.

## Relationship to the broader OSS naming world

The early naming research deliberately explored whale, Arctic, ocean, boundary, movement, sensing, and feedback concepts. Many obvious names were already strongly occupied by GitHub projects, AI products, or robotics research.

The important outcome was not only the final name. The search clarified the project's identity:

- another whale name would make the project feel like a sibling by mascot alone
- hardware/vendor words would age poorly
- `edge`, `physical`, `robot`, `agent`, `sense`, and similar direct technical names were heavily saturated
- boundary, movement, current, loop, and environment were stronger conceptual anchors
- an Arctic identity could connect naturally with the existing ecosystem without forcing another animal name

Siqoq became a fit because its drifting-snow metaphor emphasizes **movement across environments** while preserving the Arctic character.

## Relationship to Narwhal and Beluga

Siqoq is intended to coexist with the wider OSS ecosystem rather than copy naming patterns mechanically.

```text
Narwhal
  Cloud Native / platform-oriented infrastructure

Beluga
  Data-platform-oriented infrastructure

Siqoq
  Simulation → Edge → Physical AI experimentation
```

The common thread is not that every project must be another whale. The common thread is a recognizable Arctic/ocean ecosystem with distinct technical responsibilities.

## Guiding sentence

> **Build in simulation. Run at the edge. Move into the physical world.**

If a proposed feature does not improve this path, make it safer, make it more observable, or make it more portable, it should be questioned before entering the core project.
