# Siqoq

[English](README.md) | **한국어**

> 노트북의 시뮬레이션에서 시작해 엣지 장치와 실제 센서까지 이어지는 Physical AI 실험 인프라.

## 이름과 발음

**Siqoq**은 프로젝트 이름으로 **시콕**이라고 읽습니다.

이 이름은 북극권의 눈과 바람에서 영감을 받았으며, 프로젝트에서는 **바람에 흩날리며 이동하는 눈(drifting snow)**의 이미지를 상징적으로 사용합니다. 특정 언어권의 의미를 과도하게 단정하기보다는, 시뮬레이션에서 시작한 AI 워크로드가 노트북, 엣지 장치, 실제 물리 환경으로 이동한다는 프로젝트 철학을 표현하는 이름으로 사용합니다.

> **Build in simulation. Run at the edge. Move into the physical world.**
>
> 시뮬레이션에서 만들고, 엣지에서 실행하고, 실제 물리 세계로 확장합니다.

## Siqoq이 해결하려는 문제

Physical AI를 실험하려고 하면 카메라, GPU 보드, 로봇, LiDAR 같은 하드웨어부터 준비해야 하는 경우가 많습니다. 이 방식은 초기 학습과 소프트웨어 검증을 하드웨어 조달과 장치별 SDK에 지나치게 종속시킵니다.

Siqoq은 순서를 반대로 가져갑니다.

1. 노트북에서 녹화 영상, 가상 센서, 시뮬레이션으로 시작합니다.
2. 가상 센서와 실제 센서가 같은 계약(contract)을 사용하도록 합니다.
3. perception과 inference 결과를 장치별 raw data가 아닌 semantic event로 변환합니다.
4. 동일한 워크로드를 x86/ARM/NVIDIA Jetson 같은 엣지 환경으로 이동합니다.
5. 입력 → 추론 → 판단 → 행동 전체 경로를 관측할 수 있게 합니다.
6. 소프트웨어 경로가 검증된 이후 실제 actuator와 robot을 연결합니다.

## 프로젝트 범위

Siqoq은 새로운 로봇 프레임워크나 AI 학습 프레임워크를 만드는 프로젝트가 아닙니다. 기존 생태계를 연결하면서 **Simulation → Perception → Edge → Action** 사이의 이식 가능한 계약과 실행 인프라에 집중합니다.

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

## 현재 구현된 스켈레톤

아키텍처를 문서로만 두지 않기 위해 외부 하드웨어나 추가 라이브러리가 없어도 실행되는 최소 골격을 구현했습니다.

- vendor-neutral `SensorSample`, `Detection`, `ActionRequest`, `ActionResult` contract
- `SensorAdapter`, `InferenceAdapter`, `EventTransport`, `Policy`, `SafetyGate`, `ActionAdapter` protocol
- generated sensor + deterministic static inference
- versioned semantic event envelope
- in-memory event transport
- perception → event → policy → safety → action pipeline
- safe-by-default `NoOpPolicy` 및 allow-list safety gate
- 실제 장비를 건드리지 않는 mock action adapter
- runtime manifest + 기본 capability discovery
- `siqoq demo` hardware-free pipeline demo
- `siqoq inspect` runtime/capability inspection
- pipeline, safety boundary, runtime 자동화 테스트

현재 구현은 public API를 확정한 것이 아니라 실제 adapter와 runtime을 붙이기 위한 **contract-first skeleton**입니다.

## 핵심 설계 원칙

- **Simulation first** — 실제 장비가 없어도 핵심 흐름을 개발하고 테스트할 수 있어야 합니다.
- **Hardware optional** — Jetson은 중요한 실행 대상이지만 Siqoq 자체가 Jetson 전용 플랫폼이 되지 않습니다.
- **Stable contracts** — simulator와 real device가 downstream 코드를 갈아엎지 않고 교체될 수 있어야 합니다.
- **Semantic events** — 가능한 경우 raw stream보다 의미가 정규화된 event를 플랫폼 경계로 사용합니다.
- **Portable inference** — CPU baseline을 유지하고 accelerator는 adapter/profile로 추가합니다.
- **Observable decisions** — sensor, inference, decision, action을 하나의 trace로 추적할 수 있어야 합니다.
- **Safe actuation** — AI reasoning이 모터나 GPIO를 직접 제어하지 않고 명시적인 action/safety boundary를 통과합니다.
- **Cloud-native where useful** — container, declarative configuration, GitOps, observability를 필요한 단계에서 도입하되 Kubernetes를 필수 조건으로 만들지 않습니다.

## MVP

첫 번째 목표는 로봇을 움직이는 것이 아니라 **하드웨어 없이 전체 software loop를 증명하는 것**입니다.

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

그 다음 같은 계약을 사용해 Jetson과 실제 센서로 이동합니다.

## 단계적 하드웨어 전략

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

## Siqoq이 대체하지 않는 것

Siqoq은 ROS 2, Isaac Sim, Gazebo, Kubernetes, 모델 학습 프레임워크, 모델 레지스트리, 하드웨어 SDK를 대체하려 하지 않습니다. 이들과 adapter/bridge 형태로 통합하면서 simulation-to-edge 경로를 일관되게 만드는 데 집중합니다.

## 문서

영문 문서를 기준 문서로 유지하면서 주요 문서는 한국어 버전을 함께 제공합니다.

- [Vision](docs/vision.md) / [비전](docs/vision.ko.md)
- [Architecture](docs/architecture.md) / [아키텍처](docs/architecture.ko.md)
- [Roadmap](docs/roadmap.md) / [로드맵](docs/roadmap.ko.md)
- [Development Guide](docs/development.md) / [개발 가이드](docs/development.ko.md)
- [Project name](docs/project-name.md) / [프로젝트명](docs/project-name.ko.md)
- [OSS landscape](docs/landscape.md) / [OSS 생태계](docs/landscape.ko.md)
- [Contract specs](docs/specs/README.md) / [Contract 명세](docs/specs/README.ko.md)
- [Project Principles](docs/principles.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## 현재 상태

**Early bootstrap / architecture validation** 단계입니다. 큰 프레임워크를 먼저 만들기보다 작은 실행 코어와 명확한 계약을 검증하고, 검증된 경계부터 단계적으로 확장합니다.

## 라이선스

Apache License 2.0. 자세한 내용은 [LICENSE](LICENSE)를 참고하세요.
