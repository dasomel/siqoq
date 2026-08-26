# Siqoq 비전

[English](vision.md) | **한국어**

## Siqoq은 왜 시작했는가

Siqoq의 출발점은 아주 현실적인 질문이었습니다.

> **Physical AI를 실험하려면 처음부터 비싼 전용 하드웨어가 꼭 필요한가?**

처음에는 이미지/영상 입력과 간단한 Edge AI 실험에서 시작했습니다.

```text
이미지 / 영상 입력
      ↓
   Vision AI
      ↓
 Semantic Event
      ↓
  Edge Runtime
      ↓
선택적 Physical Action
```

Jetson, 카메라, 센서, 로봇, 시뮬레이터, Physical AI OSS를 계속 조사하면서 프로젝트 방향은 더 명확해졌습니다. Siqoq은 **Jetson 데모도 아니고, 또 하나의 로봇 프레임워크도 아닙니다.**

핵심은 디지털 환경에서 검증한 AI workload를 실제 물리 환경으로 안전하고 일관되게 이동시키는 경로입니다.

## 핵심 개념 — Digital ↔ Physical Boundary

네이밍과 프로젝트 방향을 함께 고민하면서 가장 중요하게 남은 개념은 **디지털 세계와 물리 세계의 경계**였습니다.

```text
Digital World
  Simulation / Recorded Data / Model / Agent
                 │
                 │  Stable Contracts
                 ▼
               SIQOQ
                 │
                 │  Sensor / Event / Action Adapter
                 ▼
Physical World
  Camera / Edge Device / Actuator / Robot
```

Physical AI의 핵심은 단순히 모델을 한 번 실행하는 것이 아니라 이 경계를 반복적으로 넘나드는 것입니다.

따라서 Siqoq은 이 경계에서 다음을 지키는 것을 중요하게 봅니다.

- 입력과 출력의 의미가 유지되는가
- simulator와 real device를 바꿔도 contract가 유지되는가
- 어떤 판단이 어떤 행동으로 이어졌는지 추적 가능한가
- 실제 행동 전에 명시적인 safety boundary가 있는가

## 핵심 루프 — Sense → Think → Act → Feedback

Siqoq은 Physical AI를 단방향 inference pipeline이 아니라 **폐루프(closed loop)**로 봅니다.

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
  └──────────────→ Feedback to Sense
```

이 때문에 semantic event, correlation ID, action result, end-to-end trace가 중요합니다.

단순히 `객체를 감지했다`에서 끝나는 시스템은 실제 물리 환경에 영향을 줄 수 있는 순간부터 불완전합니다. **어떤 입력 → 어떤 추론 → 어떤 판단 → 어떤 safety gate → 어떤 action**으로 이어졌는지 재구성할 수 있어야 합니다.

## Simulation First, Hardware Later

초기 리서치에서 카메라가 가장 접근하기 쉬운 Physical AI 입력이라는 판단이 있었지만, 그보다 더 중요한 결론은 **실제 장비를 구입하기 전에 에뮬레이션/시뮬레이션으로 소프트웨어 경로를 검증할 수 있어야 한다**는 점이었습니다.

Siqoq은 현실성을 단계적으로 도입합니다.

1. generated / recorded data
2. laptop + USB webcam
3. deterministic simulator
4. Jetson 같은 edge accelerator
5. depth camera / LiDAR / IMU
6. mock actuator
7. 제한된 physical actuation
8. mobile robot 또는 더 복잡한 physical system

목표는 하드웨어를 피하는 것이 아닙니다. **소프트웨어 contract와 observability가 먼저 검증된 상태에서 하드웨어 리스크를 도입하는 것**입니다.

## Edge는 목적지가 아니라 경계층

Jetson을 조사하면서 얻은 또 하나의 중요한 결론은 Jetson 자체가 프로젝트의 목적이 아니라는 점입니다.

Jetson은 카메라/센서 입력을 받아 로컬에서 추론하고, latency/privacy/connectivity 문제를 줄이며, 실제 action과 가까운 위치에서 AI를 실행하는 대표적인 edge target입니다.

하지만 Siqoq은 다음을 지향합니다.

```text
Laptop CPU Baseline
       ↓
ARM / x86 Edge
       ↓
Jetson / Accelerator Profile
       ↓
Real Physical System
```

따라서 Jetson은 매우 중요한 검증 대상이지만 **Siqoq = Jetson 프로젝트**가 되지는 않습니다.

## 왜 또 하나의 Robotics Framework가 아닌가

기존 OSS 리서치에서 이미 강한 생태계가 있다는 점을 확인했습니다.

- ROS 2 — robot middleware
- Isaac Sim / Gazebo — simulation
- LeRobot — dataset, policy, robot-learning workflow
- NVIDIA/Intel runtime — accelerator execution
- Kubernetes/K3s — orchestration

Siqoq이 이들을 다시 만드는 것은 가치가 낮습니다.

Siqoq이 소유해야 할 부분은 다음입니다.

- portable simulation-to-edge path
- virtual / real adapter conformance
- semantic event boundary
- end-to-end decision observability
- physical action 이전의 safety boundary
- hardware를 늦게 도입할 수 있는 developer experience

## Cloud Native는 강점이지만 출발점은 아니다

초기에는 Cloud Native 경험을 Siqoq에 바로 크게 넣을 수도 있었지만, 리서치 과정에서 **로컬/단일 노드가 먼저**라는 방향이 더 적절하다고 판단했습니다.

```text
Local First
    ↓
Edge Capable
    ↓
Cloud Optional
    ↓
Fleet When Needed
```

Kubernetes, GitOps, fleet management는 장기적으로 중요한 기능이지만 첫 사용자에게 요구되는 최소 조건이 되어서는 안 됩니다.

## 네이밍 리서치가 프로젝트 방향을 바꾼 부분

초기에는 기존 OSS와 결을 맞추기 위해 여러 고래 이름과 해양 용어를 조사했습니다.

Beluga, Orca, Minke, Bowhead, Baleen, Fluke, Tusk, Coda, Triton, Tidal, Spiral, Helix, Qajaq, Polynya, Boreal 등 다양한 이름을 검토했습니다.

많은 후보가 GitHub, AI, robotics, 기업/제품 영역에서 이미 강하게 사용되고 있었습니다.

하지만 이 과정에서 중요한 것은 **후보를 탈락시키는 것 자체가 아니라 프로젝트의 정체성이 정리된 것**입니다.

### 1. 또 다른 고래 이름일 필요는 없다

Narwhal이나 Beluga와 같은 기존 프로젝트와 결을 맞추되, 모든 프로젝트를 고래 이름으로 반복하면 기술 역할보다 mascot 관계가 더 강하게 보일 수 있습니다.

### 2. 직접적인 기술 단어는 너무 포화되어 있다

`Edge`, `Physical`, `Robot`, `Agent`, `Sense`, `Current`, `Field`, `Loop` 같은 이름은 이미 다양한 기술 프로젝트에서 광범위하게 사용되고 있었습니다.

### 3. 더 중요한 개념은 Boundary / Movement / Feedback이었다

네이밍을 좁히면서 결국 다음 개념들이 프로젝트 본질과 더 잘 맞았습니다.

- Digital ↔ Physical boundary
- Simulation ↔ Reality
- movement across environments
- perception-action feedback loop
- edge as a bridge
- Arctic ecosystem identity

Siqoq은 이 중 **movement + Arctic** 이미지를 가장 잘 남길 수 있는 이름이었습니다.

## Narwhal / Beluga와의 관계

Siqoq은 기존 프로젝트와 세계관을 공유하지만 역할은 명확히 다르게 가져갑니다.

```text
Narwhal
  Cloud Native / Platform Infrastructure

Beluga
  Data Platform

Siqoq
  Simulation → Edge → Physical AI
```

공통점은 모든 프로젝트가 같은 동물 이름을 써야 한다는 것이 아니라, **북극/해양 계열의 일관된 OSS 세계관 안에서 서로 다른 엔지니어링 문제를 해결한다는 점**입니다.

## 프로젝트를 판단하는 한 문장

> **Build in simulation. Run at the edge. Move into the physical world.**
>
> **시뮬레이션에서 만들고, 엣지에서 실행하고, 실제 물리 세계로 확장한다.**

새 기능이 이 경로를 더 portable하게 만들거나, 더 observable하게 만들거나, 더 safe하게 만들지 못한다면 core에 들어가기 전에 다시 검토해야 합니다.
