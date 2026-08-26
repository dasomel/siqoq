# Physical AI OSS 생태계 분석

[English](landscape.md) | **한국어**

이 문서는 Siqoq가 참고하거나 통합해야 할 기존 프로젝트와, 굳이 다시 만들지 말아야 할 영역을 정리합니다. 경쟁 순위가 아니라 **프로젝트 범위를 명확히 유지하기 위한 설계 참고 문서**입니다.

## Siqoq의 포지션

Siqoq은 새로운 종합 로봇 학습 플랫폼, agent runtime, simulator, cloud control plane을 만들려는 프로젝트가 아닙니다.

핵심은 다음과 같습니다.

> **Physical AI 실험을 위한 simulation-to-edge 계약과 실행 인프라. Semantic event, observability, 그리고 physical action 전의 명시적 safety boundary를 제공한다.**

## Microsoft Physical AI Toolchain

참고: https://github.com/microsoft/physical-ai-toolchain

이미 잘하는 것:

- laptop-first T0 개발 경로
- T0~T5 단계형 adoption model
- Jetson edge capture/inference
- Isaac Sim / Isaac Lab 연동
- LeRobot 기반 training/evaluation
- ONNX/TensorRT 배포
- k3s/GitOps 및 multi-site fleet 확장
- Azure 기반 cloud training/enterprise 운영

Siqoq이 배울 점:

- 하나의 거대한 stack보다 **단계형 maturity model**을 사용
- laptop → lab → edge → fleet의 graduation trigger를 문서화
- Kubernetes/cloud는 실제 규모가 필요할 때만 도입

Siqoq이 다시 만들지 않을 것:

- Azure infrastructure provisioning
- 전체 training lifecycle orchestration
- enterprise federation/control plane

## Open Edge Platform — Physical AI Studio

참고: https://github.com/open-edge-platform/physical-ai-studio

이미 잘하는 것:

- imitation-learning end-to-end workflow
- VLA/policy training
- GUI/Python API/CLI
- OpenVINO/ONNX/Torch export
- benchmark 기반 평가

Siqoq이 배울 점:

- 로컬 사용자의 진입점을 단순하게 유지
- 재현 가능한 demo/benchmark scenario 제공
- inference backend를 교체 가능하게 유지

다시 만들지 않을 것:

- policy training framework
- VLA model zoo
- robot-learning GUI 자체를 core product로 만드는 것

## Hugging Face LeRobot

참고: https://github.com/huggingface/lerobot

이미 잘하는 것:

- 표준화된 robot dataset
- teleoperate → record → train → deploy 흐름
- 다양한 robot/policy 생태계
- simulation evaluation
- 실제 robot policy deployment CLI
- third-party policy plugin 구조

Siqoq에서 고려할 것:

- LeRobot dataset/policy를 optional integration으로 지원
- 이미 존재하는 policy deployment 생태계를 재사용
- out-of-tree adapter/plugin 방식 참고
- 외부 model/policy artifact 다운로드 시 security rule 강화

다시 만들지 않을 것:

- 새로운 robot dataset format
- 자체 robot policy zoo
- imitation/RL/VLA training stack

## OpenRAL

참고: https://github.com/OpenRAL/openral

OpenRAL은 hardware, sensor, world state, skill, reasoning, safety, observability 사이를 typed contract로 나누는 safety-first Robot Agentic Layer를 지향합니다.

Siqoq이 배울 점:

- boundary별 typed/versioned contract
- safety와 observability를 부가기능이 아닌 architecture layer로 취급
- 빠른 control/policy와 느린 reasoning path 분리

겹칠 수 있는 영역:

- perception/world-state/action contract
- safety
- observability
- runtime abstraction

Siqoq의 차별점:

- complete robot-agent runtime보다 **simulation-to-edge portability/infrastructure**에 집중
- agent reasoning은 optional
- semantic event transport와 edge/fleet operations를 first-class concern으로 유지

## Physical AI Harness

참고: https://github.com/nanxintin/physical-ai-harness

특징:

- simulator와 real device를 standardized interface로 노출
- LLM agent가 physical device를 사용할 수 있게 함
- MCP를 주요 agent/device interface로 사용

Siqoq이 배울 점:

- simulator/real-device parity는 중요
- 향후 MCP adapter는 agent integration에 유용할 수 있음

피해야 할 것:

- MCP/LLM agent를 core runtime의 필수 의존성으로 만드는 것
- agent tool call이 safety/action boundary 없이 실제 hardware를 직접 제어하는 구조

## NVIDIA Isaac Sim / Isaac Lab / OSMO

NVIDIA stack은 중요한 integration target이지만 Siqoq core architecture를 정의하는 필수 의존성으로 만들지 않습니다.

가능한 통합:

- Isaac Sim virtual sensor adapter
- deterministic simulation scenario
- Isaac Lab/LeRobot 결과물의 optional policy artifact 활용
- TensorRT edge inference profile

Sensor/Event/Action contract는 NVIDIA 소프트웨어가 없어도 사용할 수 있어야 합니다.

## ROS 2

ROS 2는 많은 sensor, robot, navigation stack, hardware interface를 연결하는 표준적인 통합 지점입니다.

Siqoq의 입장:

- ROS 2 bridge/adapter: 지원
- laptop MVP에서 ROS 2 필수: 아님
- ROS 2 대체: 아님
- core event/domain contract를 ROS message에 종속: 아님

## Siqoq이 노리는 빈 공간

현재 생태계에는 이미 다음 영역의 강한 OSS가 있습니다.

- simulation
- robot learning/training
- dataset/model sharing
- ROS hardware integration
- agent runtime
- cloud-scale operation

Siqoq은 그 사이의 더 작은 연결 계층을 실험합니다.

```text
저비용 local experiment
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

사용자가 robot을 사기 전에도, cloud를 선택하기 전에도, agent framework를 선택하기 전에도 유용한 프로젝트를 목표로 합니다.

## Reuse-before-build 규칙

새 subsystem을 만들기 전에 다음을 확인합니다.

1. 이미 이 문제를 잘 해결하는 성숙한 OSS가 있는가?
2. 직접 구현 대신 adapter로 연동할 수 있는가?
3. 이 기능이 Siqoq의 simulation-to-edge contract/runtime 범위에 속하는가?
4. laptop-first 경로에서는 optional로 유지할 수 있는가?
5. 실제 hardware 없이 테스트할 방법이 있는가?

1, 2가 `예`이고 3이 `아니오`라면 **재구현보다 integration을 우선**합니다.
