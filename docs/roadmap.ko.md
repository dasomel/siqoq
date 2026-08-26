# Siqoq 로드맵

[English](roadmap.md) | **한국어**

로드맵의 기본 원칙은 **소프트웨어 계약을 먼저 검증하고 하드웨어 의존성을 단계적으로 추가하는 것**입니다.

## Phase 0 — Bootstrap

목표: OSS 프로젝트로서 지속적으로 개발할 수 있는 최소 기반을 만듭니다.

- OpenForge 스타일 OSS 구조
- 영문/한글 README 및 핵심 문서
- architecture / principles / development guide
- CI, issue/PR template, dependency hygiene
- 하드웨어가 필요 없는 executable demo
- issue-driven development

**Exit criteria:** 새 contributor가 노트북에서 clone → install → test → demo까지 수행할 수 있습니다.

## Phase 1 — Laptop-first Vision MVP

목표: 특수 장비 없이 perception → semantic event → observability 경로를 증명합니다.

- recorded video adapter
- USB webcam adapter
- OpenCV preprocessing
- ONNX Runtime inference adapter
- semantic event schema v0
- stdout/in-memory transport
- NATS/MQTT transport
- OpenTelemetry baseline
- pipeline CLI

**대표 데모:** 노트북 webcam/video에서 객체를 감지하고 `object.detected` event를 발행하며 inference latency와 event trace를 확인합니다.

## Phase 2 — Simulation First

목표: 실제 하드웨어를 구입하기 전에 virtual sensor와 action path를 검증합니다.

- common simulation adapter contract
- simulated camera
- deterministic scenes/fixtures
- Isaac Sim integration spike
- Gazebo integration spike
- simulation ↔ real sensor compatibility tests
- mock actuator loop

**Exit criteria:** 동일한 downstream pipeline이 recorded data, simulator, real webcam을 설정 변경만으로 사용할 수 있습니다.

## Phase 3 — Edge Runtime

목표: 노트북에서 검증된 workload를 edge hardware로 옮깁니다.

- device capability discovery
- ARM64 container build
- NVIDIA Jetson profile
- TensorRT adapter
- accelerator/GPU metrics
- reproducible deployment bundle
- CPU fallback 유지

**대표 검증:** 동일 모델과 semantic event contract가 laptop과 Jetson에서 동작하고 성능 차이를 telemetry로 비교합니다.

## Phase 4 — Physical Action / Robotics Bridge

목표: AI decision을 안전한 physical action으로 연결합니다.

- ROS 2 bridge
- mock actuator
- GPIO/relay adapter
- MCU/motor-controller boundary
- action policy/safety gate
- depth/LiDAR/IMU adapter
- timeout / allow-list / range validation

**원칙:** reasoning component는 실제 hardware를 직접 제어하지 않습니다.

## Phase 5 — Cloud-native Operations

목표: 단일 edge node에서 검증된 runtime을 여러 장치로 확장합니다.

- optional K3s/Kubernetes deployment
- declarative workload spec
- GitOps deployment
- model/workload rollout & rollback
- edge inventory
- device capability 기반 placement
- fleet telemetry

Kubernetes는 laptop/single-node 사용자의 필수 의존성이 되지 않습니다.

## Phase 6 — Physical AI Experimentation Platform

목표: 안정화된 core contract 위에 고수준 실험 기능을 추가합니다.

- semantic skill/event catalog
- local/cloud AI routing
- agent/policy integration
- simulation CI
- digital-twin validation workflow
- end-to-end decision trace
- fleet-level AI observability
- benchmark/scenario catalog

## 하드웨어 도입 순서

1. Laptop + generated/recorded data — 비용 0에 가까운 시작점
2. Laptop + USB webcam — 실제 sensor input
3. Simulator — 반복 가능한 virtual physical environment
4. Jetson Orin Nano-class edge — accelerator와 ARM64 검증
5. Depth camera / LiDAR / IMU — multimodal perception
6. Relay/MCU — 제한된 physical action
7. Small mobile robot — perception-action closed loop

하드웨어 자체를 검증하는 기능이 아니라면 테스트와 기본 개발 흐름은 특정 장비를 요구하지 않아야 합니다.

## 장기 성공 기준

Siqoq의 성공은 지원 장비 수만으로 측정하지 않습니다. 다음 질문에 `예`라고 답할 수 있는지를 더 중요하게 봅니다.

- 하드웨어 없이 시작할 수 있는가?
- simulator와 real sensor 사이에서 application logic을 재작성하지 않아도 되는가?
- laptop에서 검증한 workload를 edge로 이동할 수 있는가?
- perception부터 action까지 원인을 추적할 수 있는가?
- AI가 실제 장치를 직접/무제한으로 제어하지 않는가?
- 특정 vendor, simulator, orchestrator 없이도 core contract가 유지되는가?
