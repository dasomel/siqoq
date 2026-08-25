# Roadmap

## Phase 0 — Bootstrap

- OpenForge-aligned OSS structure
- README, architecture, principles, development guide
- CI and contribution templates
- executable local demo
- issue-driven development

## Phase 1 — Laptop-first vision demo

Goal: prove the full perception → event → observability path without special hardware.

- recorded video input
- USB webcam input
- OpenCV preprocessing
- ONNX Runtime inference adapter
- semantic event schema
- stdout/in-memory event transport
- NATS transport
- OpenTelemetry baseline
- CLI for running the pipeline

## Phase 2 — Simulation adapters

- simulated camera adapter
- Isaac Sim integration spike
- Gazebo integration spike
- deterministic test scenes
- simulation/real sensor compatibility tests

## Phase 3 — Edge runtime

- device capability discovery
- ARM64 container builds
- NVIDIA Jetson profile
- TensorRT inference adapter
- GPU/accelerator metrics
- reproducible deployment bundle

## Phase 4 — Robotics bridge

- ROS 2 bridge
- mock actuator adapter
- GPIO/relay adapter
- MCU boundary design
- action policy/safety gates
- LiDAR/depth/IMU sensor adapters

## Phase 5 — Cloud-native operations

- K3s/Kubernetes deployment option
- declarative workload specification
- GitOps deployment flow
- model/workload rollout and rollback
- edge fleet inventory
- workload routing based on hardware capability

## Phase 6 — Physical AI platform capabilities

- semantic event catalog / skill registry
- local vs cloud AI router
- agent/policy integration
- simulation CI
- digital-twin validation workflows
- end-to-end decision traces
- fleet-level AI observability

## Hardware strategy

Hardware is introduced incrementally:

1. laptop + recorded video
2. laptop + USB webcam
3. Jetson Orin Nano-class device
4. depth camera / LiDAR
5. relay or MCU-controlled actuator
6. small mobile robot

A feature should not require hardware unless its purpose is specifically hardware validation.
