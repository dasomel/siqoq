# Siqoq 아키텍처

[English](architecture.md) | **한국어**

Siqoq은 **simulation-to-reality 경로를 안정적인 계약으로 연결하는 것**을 핵심 아키텍처 원칙으로 합니다.

## 핵심 루프

```text
Simulation / Sensor
        ↓
    Perception
        ↓
   World State
        ↓
 Reason / Policy
        ↓
      Action
        ↓
 Physical World
        └──────────────→ Feedback
```

이 루프에서 simulator, sensor, inference engine, actuator는 바뀔 수 있지만 각 단계 사이의 계약은 가능한 한 안정적으로 유지합니다.

## 1. Sensor Adapter Layer

가상 센서와 실제 센서의 입력 차이를 adapter에서 흡수합니다.

초기 대상은 recorded video, USB/UVC webcam, simulated camera입니다. 이후 CSI camera, LiDAR, depth camera, IMU, audio로 확장합니다.

핵심 규칙은 downstream pipeline이 입력이 simulator인지 실제 카메라인지 알 필요가 없도록 하는 것입니다.

## 2. Perception / Inference Runtime

특수 가속기가 없는 일반 노트북에서 동작하는 CPU baseline을 먼저 유지합니다.

- Baseline: OpenCV + ONNX Runtime
- NVIDIA acceleration: TensorRT
- 기타 ARM/x86 accelerator: adapter/profile 방식으로 확장

가속기 전용 구현이 core domain contract로 유입되지 않도록 합니다.

## 3. Semantic Event Layer

raw frame이나 vendor-specific inference result를 플랫폼의 장기 API로 사용하지 않습니다. perception 결과를 의미 중심의 event로 정규화합니다.

```json
{
  "type": "object.detected",
  "source": "camera.front",
  "object": "person",
  "confidence": 0.94,
  "timestamp": "..."
}
```

이를 통해 downstream consumer는 카메라 SDK나 모델별 tensor 형식보다 `무엇이 감지되었는가`에 집중할 수 있습니다.

## 4. Event Transport

semantic event의 transport는 교체 가능해야 합니다.

초기에는 in-process/stdout을 사용하고, 이후 NATS와 MQTT를 지원합니다. transport 기술 자체가 domain model이 되지 않도록 합니다.

## 5. World State / Policy / Agent

semantic event를 이용해 현재 환경 상태를 구성하고 다음 행동을 결정합니다. 이 계층은 deterministic rule, policy engine, local AI, optional cloud AI 등을 사용할 수 있습니다.

**LLM이나 VLM은 선택 사항이며 Siqoq core가 동작하기 위한 필수 조건이 아닙니다.**

## 6. Action & Safety Boundary

reasoning 결과가 실제 장치를 직접 호출하지 않습니다.

```text
Decision
   ↓
Action Request
   ↓
Policy / Safety Gate
   ↓
Action Adapter
   ↓
Mock / GPIO / MCU / ROS 2
   ↓
Physical Device
```

초기에는 mock actuator를 사용해 CI와 노트북에서 행동 경로를 검증합니다. 실제 장비 연결 시 timeout, allow-list, range validation, emergency stop 같은 안전 정책을 단계적으로 도입합니다.

## 7. Observability

다음 전체 경로를 하나의 trace로 연결하는 것을 목표로 합니다.

```text
sensor read
 → preprocessing
 → inference
 → semantic event
 → world-state update
 → policy decision
 → action request
 → safety gate
 → action result
```

OpenTelemetry를 기본 telemetry model로 사용하고 Prometheus/Grafana와 연동 가능한 metrics를 제공합니다.

중요한 원칙은 **AI가 무엇을 판단했는지뿐 아니라 어떤 입력과 정책을 거쳐 실제 행동 요청으로 이어졌는지를 재구성할 수 있는 것**입니다.

## 실행 모드

### Laptop Mode

특수 장비 없이 개발하는 기본 모드입니다. recorded data/webcam, CPU inference, local event transport, local observability를 사용합니다.

### Simulation Mode

Isaac Sim/Gazebo 등의 virtual sensor를 동일 Sensor API에 연결합니다. deterministic scene/fixture를 사용해 regression test와 향후 simulation CI 기반을 만듭니다.

### Edge Mode

Jetson/ARM/x86 장치에서 실제 sensor와 accelerator를 사용합니다. Laptop Mode와 semantic contract를 유지하면서 device-specific optimization만 profile로 추가합니다.

### Fleet Mode

단일 edge node가 안정화된 이후의 장기 모드입니다. declarative configuration, container registry, GitOps, optional K3s/Kubernetes를 이용해 여러 edge node의 workload와 model을 관리합니다.

## 핵심 컴포넌트 경계

```text
siqoq-core
  ├─ domain contracts
  ├─ semantic events
  └─ action contracts

adapters
  ├─ sensors
  ├─ inference
  ├─ transports
  ├─ simulators
  └─ actuators

runtime
  ├─ pipeline orchestration
  ├─ configuration
  ├─ capability discovery
  └─ lifecycle

observability
  ├─ traces
  ├─ metrics
  └─ structured logs
```

향후 실제 package layout은 구현 경험을 통해 검증한 뒤 확정하며, 초기 단계에서 지나치게 많은 microservice로 분리하지 않습니다.

## Non-goals

Siqoq은 다음을 대체하지 않습니다.

- ROS 2
- Isaac Sim / Gazebo
- PyTorch 등 model training framework
- Kubernetes
- model registry
- robot vendor SDK

Siqoq의 역할은 이들을 하나로 다시 만드는 것이 아니라 **simulation에서 실제 edge/physical environment로 이동할 때 필요한 안정적인 경계와 실행 경로를 제공하는 것**입니다.
