# Siqoq

**English** | [한국어](README.ko.md)

> Simulation-first infrastructure for Physical AI — from a laptop to edge devices and real-world sensors.

**Build in simulation. Run at the edge. Move into the physical world.**

Siqoq is an open-source experimentation infrastructure for building and validating Physical AI workflows without requiring physical hardware on day one. It provides a progressive path from generated or recorded data and virtual sensors to real cameras, edge accelerators, and eventually safe physical actuation.

## Name and pronunciation

**Siqoq** is pronounced **“see-kok”** (Korean: **시콕**) for the project.

The name is inspired by Arctic snow and wind imagery, especially the idea of **drifting snow**. Siqoq uses that image as a project metaphor: an AI workload should be able to move from simulation to a laptop, from a laptop to an edge device, and from the digital environment into the physical world without rewriting its core application contracts.

Arctic Indigenous languages are diverse, so the project does not present the name as a universal translation across Inuit languages or dialects. See [Project name and pronunciation](docs/project-name.md) for the preferred wording and linguistic note.

## The problem

Physical AI experimentation often becomes hardware-dependent too early. A developer may need a GPU board, camera, robot, LiDAR, or vendor SDK before validating even the basic software path. This raises cost, slows iteration, makes CI difficult, and couples application logic to hardware-specific APIs.

Siqoq intentionally reverses that order:

1. Start on a laptop with generated data, recorded media, virtual sensors, or simulation.
2. Keep stable contracts between simulated and physical sensors.
3. Normalize perception output into semantic events rather than exposing device-specific raw streams as the platform API.
4. Run AI workloads behind portable inference adapters.
5. Move the same workload to x86, ARM, NVIDIA Jetson, or other edge targets.
6. Trace the complete perception → decision → action path.
7. Introduce physical actuation only after the software path has been validated.

## What Siqoq is

Siqoq focuses on the **simulation-to-edge execution path and the contracts between perception and physical action**.

```text
Simulation / Recorded Data
            │
            ▼
      Sensor Adapter
            │
      ┌─────┴─────┐
      ▼           ▼
 Virtual       Physical
 Sensor         Sensor
      └─────┬─────┘
            ▼
     Perception / AI
            │
            ▼
      Semantic Event
            │
            ▼
       Policy / Agent
            │
            ▼
       Action Adapter
            │
            ▼
      Physical World
            │
            └──────── feedback ────────┐
                                       │
                 Observability ◀───────┘
```

It is intended to be useful at several maturity levels:

- **Laptop:** generated/recorded data, webcam, CPU inference
- **Simulation:** virtual sensors and deterministic scenarios
- **Edge:** Jetson, ARM, x86 and accelerator-specific profiles
- **Physical:** sensors, MCU/GPIO, ROS 2 bridges and robots
- **Fleet:** optional declarative deployment, GitOps and Kubernetes/K3s

## Current implementation skeleton

The architecture is no longer documentation-only. A dependency-light, hardware-free skeleton now provides the first executable boundaries:

- vendor-neutral `SensorSample`, `Detection`, `ActionRequest`, and `ActionResult` contracts
- `SensorAdapter`, `InferenceAdapter`, `EventTransport`, `Policy`, `SafetyGate`, and `ActionAdapter` protocols
- generated sensor + deterministic static inference
- versioned semantic-event envelope
- in-memory transport
- perception → event → policy → safety → action pipeline
- safe-by-default `NoOpPolicy` and allow-list safety gate
- mock action adapter that never touches physical hardware
- runtime manifest and baseline capability discovery
- `siqoq demo` hardware-free pipeline demo
- `siqoq inspect` runtime/capability inspection
- tests for the pipeline, safety boundary, and runtime bootstrap

These are implementation scaffolds rather than frozen public APIs. The next step is to evolve them through versioned specifications and shared adapter conformance tests.

## Design principles

- **Simulation first** — hardware must not block core development or testing.
- **Hardware optional, not hard-coded** — Jetson is an important target, not the platform itself.
- **Stable contracts** — simulated and real implementations should be interchangeable without rewriting downstream application logic.
- **Semantic events over raw streams** — expose meaning at platform boundaries where practical.
- **Portable inference** — preserve a CPU baseline and add accelerators through adapters/profiles.
- **Observable decisions** — correlate sensor input, inference, decisions, safety checks, and action results.
- **Safe physical boundary** — reasoning does not directly control physical hardware; actions pass through explicit adapters and policy/safety gates.
- **Cloud-native where useful** — use containers, declarative configuration, GitOps, and observability when they solve a real operational problem, without making Kubernetes mandatory.
- **Integration over replacement** — work with ROS 2, simulators, model runtimes, and hardware SDKs rather than rebuilding them.
- **Reuse before build** — integrate mature OSS through adapters when another project already owns the problem well.

## Initial MVP

The first milestone deliberately avoids robotics hardware. Its purpose is to prove the complete software path:

```text
video / webcam / simulated camera
              ↓
        vision inference
              ↓
        semantic event
              ↓
        NATS / MQTT
              ↓
     API + observability
```

The same sensor, event, and action contracts will then be reused as the project moves to simulation, Jetson-class devices, and real physical systems.

## Progressive hardware strategy

```text
Laptop + generated/recorded data
              ↓
Laptop + USB webcam
              ↓
Simulation (Isaac Sim / Gazebo)
              ↓
Jetson / ARM / x86 edge
              ↓
Depth camera / LiDAR / IMU
              ↓
Mock actuator → MCU / ROS 2
              ↓
Small mobile robot
```

A feature should not require physical hardware unless the feature exists specifically to validate that hardware.

## Non-goals

Siqoq is not intended to replace:

- ROS 2
- Isaac Sim or Gazebo
- LeRobot or robot-policy training frameworks
- Kubernetes
- model registries
- robot/vendor hardware SDKs
- complete robot-agent runtimes

Instead, it integrates them where useful and focuses on keeping the path from simulation to edge and physical execution portable, observable, and testable.

## Documentation

Core documentation is maintained in English and Korean.

- [Vision](docs/vision.md) / [비전](docs/vision.ko.md)
- [Project name & pronunciation](docs/project-name.md) / [프로젝트명·발음·의미](docs/project-name.ko.md)
- [Physical AI OSS landscape](docs/landscape.md) / [Physical AI OSS 생태계](docs/landscape.ko.md)
- [Architecture](docs/architecture.md) / [아키텍처](docs/architecture.ko.md)
- [Roadmap](docs/roadmap.md) / [로드맵](docs/roadmap.ko.md)
- [Development guide](docs/development.md) / [개발 가이드](docs/development.ko.md)
- [Contract specs](docs/specs/README.md) / [Contract 명세](docs/specs/README.ko.md)
- [Project principles](docs/principles.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

English is the canonical technical reference for international collaboration. Korean documentation may add explanatory context, but behavior, interfaces, commands, and project status should remain consistent between languages.

## OSS engineering

Siqoq follows the engineering conventions maintained in OpenForge: documentation-first changes, small reviewable issues, CI from the beginning, dependency hygiene, security reporting, contribution guidance, and reproducible development workflows.

## Status

**Early bootstrap / architecture validation.**

The repository intentionally starts with a small executable core and explicit issues instead of committing to a large framework before its contracts have been validated.

## License

Apache License 2.0. See [LICENSE](LICENSE).
