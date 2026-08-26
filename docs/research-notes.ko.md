# 외부 OSS 리서치 노트

이 문서는 Siqoq 로드맵에 영향을 주는 빠르게 변하는 외부 프로젝트를 기록합니다. 생태계가 의미 있게 바뀌면 갱신합니다.

## 2026-08 검토

### Microsoft Physical AI Toolchain

- 저장소: https://github.com/microsoft/physical-ai-toolchain
- 핵심 패턴: T0~T5 단계형 adoption model
- T0은 cloud/Kubernetes 없이 local에서 시작하고, 이후 storage, training, k3s/GitOps, fleet delivery/intelligence를 단계적으로 추가
- Siqoq 적용점: 처음부터 모든 기능을 켜기보다 **각 단계의 graduation criteria를 명확히 정의**

### Open Edge Platform Physical AI Studio

- 저장소: https://github.com/open-edge-platform/physical-ai-studio
- 핵심 패턴: CLI/API/GUI와 여러 export backend를 제공하는 end-to-end imitation-learning application
- Siqoq 적용점: training framework를 다시 만들지 않고 inference/export adapter와 reproducible benchmark scenario를 강화

### Hugging Face LeRobot

- 저장소: https://github.com/huggingface/lerobot
- 핵심 패턴: standardized dataset, hardware-agnostic robot interface, simulation evaluation, policy plugin, unified rollout/deployment CLI
- 보안 교훈: 실제 장치를 제어할 수 있는 환경에서는 외부 policy/model artifact와 remote code에 대해 trust, revision pinning, safe serialization 규칙이 필요

### OpenRAL

- 저장소: https://github.com/OpenRAL/openral
- 핵심 패턴: hardware/sensor/world state/skill/reasoning/safety/observability 사이의 typed contract
- Siqoq 적용점: contract versioning, conformance test, safety, traceability를 강화하되 full robot-agent runtime과의 범위 중복은 피함

### Physical AI Harness

- 저장소: https://github.com/nanxintin/physical-ai-harness
- 핵심 패턴: simulated/real device를 통합하고 MCP를 통해 agent tool로 제공
- Siqoq 적용점: MCP는 향후 optional adapter로 검토하되 core control path로 강제하지 않고 기존 safety/action boundary를 유지

## 리서치 원칙

- 1차 출처인 공식 repository/documentation을 우선합니다.
- 빠르게 변하는 기능을 근거로 의사결정할 때는 검토 시점을 남깁니다.
- 다른 프로젝트의 architecture를 통째로 복제하지 않고 Siqoq 범위를 강화하는 패턴만 가져옵니다.
- 큰 subsystem을 새로 만들기 전에 경쟁/중복 영역을 다시 확인합니다.
