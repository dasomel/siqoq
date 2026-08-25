# Siqoq

> Simulation-first infrastructure for Physical AI — from a laptop to edge devices and real-world sensors.

Siqoq is an open-source playground and infrastructure project for experimenting with Physical AI without requiring physical hardware on day one.

The project starts with simulation and virtual sensors, then progressively moves workloads to real cameras, edge GPUs such as NVIDIA Jetson, and finally robots or actuators.

## Why Siqoq

Physical AI development often becomes hardware-dependent too early. Siqoq intentionally reverses that order:

1. Start on a laptop with simulation, recorded media, and virtual sensors.
2. Keep interfaces stable between simulated and physical sensors.
3. Run AI workloads as portable services/containers.
4. Move the same workloads to edge devices such as Jetson, ARM, or x86.
5. Observe the full perception → reasoning → action loop.
6. Add physical actuation only after the software path is validated.

## Target architecture

```text
                         ┌─────────────────────┐
                         │     Simulation      │
                         │ Isaac Sim / Gazebo  │
                         │ recorded test data  │
                         └──────────┬──────────┘
                                    │
                              Sensor API
                                    │
               ┌────────────────────┴────────────────────┐
               │                                         │
        Virtual sensors                            Real sensors
     Camera / LiDAR / IMU                    USB/CSI Camera / LiDAR
               │                                         │
               └────────────────────┬────────────────────┘
                                    │
                             Edge Runtime
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
       Vision AI                  VLM/SLM                  ROS 2
   OpenCV / YOLO / ONNX        local/cloud router       navigation I/O
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    │
                            Semantic Events
                                    │
                           NATS / MQTT / API
                                    │
                         Agent / Policy Layer
                                    │
                         Action / Actuator API
                                    │
                     Robot / relay / motor / device

                    Observability across the whole loop
                  OpenTelemetry / Prometheus / Grafana
```

## Design principles

- **Simulation first** — hardware must not block development.
- **Hardware optional, not hard-coded** — Jetson is an important target, not the platform itself.
- **Cloud-native where useful** — containers, declarative configuration, GitOps, observability.
- **Sensor abstraction** — virtual and real sensors should expose compatible interfaces.
- **Semantic events over raw streams** — edge inference should turn raw sensor data into meaningful events when possible.
- **Portable AI workloads** — laptop → x86/ARM → Jetson without rewriting application logic.
- **Observable decisions** — trace input, inference, decision, and action.
- **Safe physical boundary** — actuation is isolated behind explicit adapters and policy checks.

## Initial MVP

The first milestone deliberately avoids robotics hardware.

```text
video file / webcam / simulated camera
                ↓
          vision inference
                ↓
          semantic event
                ↓
            NATS/MQTT
                ↓
       observability + API
```

The same sensor and event contracts will later be reused for Jetson and real devices.

## Planned capabilities

- Simulation adapters: recorded media first, Isaac Sim/Gazebo later
- Sensor abstraction: camera first, LiDAR/IMU later
- Vision runtime: OpenCV + ONNX Runtime baseline, TensorRT on NVIDIA targets
- Semantic event schema and event bus
- Edge runtime and device capability discovery
- Kubernetes/K3s deployment option
- Model and workload lifecycle with declarative configuration
- OpenTelemetry metrics/traces/logs across inference and actions
- AI workload routing between local edge and optional cloud models
- ROS 2 bridge for robotics integration
- Safe actuator adapter layer
- Fleet/GitOps management after single-node MVP

## OSS engineering

Siqoq follows the engineering conventions maintained in [OpenForge](https://github.com/dasomel/openforge): documentation-first changes, small reviewable issues, CI from the beginning, dependency hygiene, security reporting, contribution guidance, and reproducible development workflows.

See:

- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Development guide](docs/development.md)
- [Project principles](docs/principles.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## Status

**Early bootstrap / architecture validation.**

The repository is intentionally starting with a small executable core and explicit issues instead of committing to a large framework before the interfaces are validated.

## License

Apache License 2.0. See [LICENSE](LICENSE).
