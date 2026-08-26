# 프로젝트 이름 — Siqoq

[English](project-name.md) | **한국어**

## 발음

Siqoq은 이 프로젝트에서 **“시콕”**이라고 읽습니다.

## 뜻과 프로젝트에서의 의미

Siqoq이라는 이름은 북극권의 눈과 바람, 특히 **바람을 따라 흩날리며 이동하는 눈(drifting snow)**의 이미지에서 영감을 받았습니다.

프로젝트에서는 이 이미지를 단순한 자연 이미지가 아니라 **환경을 옮겨 다니는 AI workload**의 은유로 사용합니다.

```text
Simulation
   ↓
Laptop
   ↓
Edge
   ↓
Physical World
```

AI workload가 하나의 환경에 고정되지 않고 시뮬레이션에서 노트북, 엣지 장치, 실제 물리 환경으로 이동하더라도 sensor, semantic event, inference, policy, observability, action에 대한 핵심 계약은 최대한 유지되어야 한다는 의미입니다.

## 네이밍 리서치에서 얻은 방향성

프로젝트명은 처음부터 Siqoq으로 정해진 것이 아닙니다. 기존 OSS와 결을 맞추기 위해 고래 이름, 북극권 단어, 해양 용어, 경계/흐름/피드백 개념까지 폭넓게 검토했습니다.

검토 과정에는 Beluga, Orca, Minke, Bowhead, Baleen, Fluke, Tusk, Coda, Triton, Tidal, Spiral, Helix, Qajaq, Polynya, Boreal 등 여러 후보가 포함되었습니다.

많은 후보가 GitHub, AI, robotics, 기업/제품 영역에서 이미 강하게 사용되고 있었습니다. 하지만 더 중요한 결과는 **프로젝트의 정체성을 명확히 한 것**이었습니다.

### 또 다른 고래 이름일 필요는 없다

Narwhal/Beluga와 같은 기존 프로젝트와 세계관은 공유하되, 모든 프로젝트를 고래 이름으로 반복하면 기술적 역할보다 mascot 관계가 더 강하게 보일 수 있습니다.

Siqoq은 같은 Arctic/ocean 계열의 감각을 유지하면서도 다른 종류의 이름을 사용합니다.

### 직접적인 기술 단어는 피한다

`Edge`, `Physical`, `Robot`, `Agent`, `Sense`, `Field`, `Loop` 같은 이름은 기술 생태계에서 지나치게 포화되어 있고 특정 시점의 기술에 프로젝트 정체성이 묶일 수 있습니다.

### 남은 핵심 개념

네이밍 탐색에서 끝까지 남은 개념은 다음이었습니다.

- Digital ↔ Physical boundary
- Simulation ↔ Reality
- movement across environments
- Sense → Think → Act → Feedback
- edge as a bridge
- Arctic ecosystem identity

Siqoq은 이 중 **movement + Arctic** 이미지를 가장 자연스럽게 담는 이름으로 선택되었습니다.

## 기존 OSS 생태계와의 관계

Siqoq은 기존 프로젝트와 같은 이름 규칙을 복제하지 않고, 역할을 분리합니다.

```text
Narwhal
  Cloud Native / Platform Infrastructure

Beluga
  Data Platform

Siqoq
  Simulation → Edge → Physical AI
```

공통점은 같은 동물 이름이 아니라 **북극/해양 계열의 일관된 세계관 속에서 각 프로젝트가 다른 엔지니어링 문제를 해결한다는 것**입니다.

## 언어학적 주의사항

북극권 원주민 언어는 하나의 단일 언어가 아니며, 지역과 언어·방언에 따라 철자와 의미가 달라질 수 있습니다.

따라서 Siqoq 프로젝트는 특정 철자가 모든 Inuit 언어에서 하나의 보편적 의미를 가진다고 단정하지 않습니다. **Siqoq은 프로젝트 고유 이름이자 북극의 이동하는 눈에서 가져온 상징적 이미지**로 사용합니다.

공개 문서나 발표에서는 다음과 같은 설명을 권장합니다.

> **Siqoq(시콕)은 북극의 drifting snow 이미지에서 영감을 받은 프로젝트 이름입니다. 시뮬레이션에서 시작한 AI workload가 엣지를 거쳐 실제 물리 환경으로 이동하는 모습을 상징합니다.**

출처 없이 특정 원주민 언어의 보편적 번역이라고 단정하거나, 해당 문화권의 용어에 대한 권위가 있는 것처럼 표현하지 않습니다.

## 브랜드 문구

> **Build in simulation. Run at the edge. Move into the physical world.**
>
> 시뮬레이션에서 만들고, 엣지에서 실행하고, 실제 물리 세계로 확장합니다.

## 아키텍처와 이름의 연결

Siqoq은 특정 하드웨어 벤더, 로봇 프레임워크, AI 모델, 클라우드 플랫폼 이름을 프로젝트명에 포함하지 않습니다. 이는 다음 장기 원칙과 맞습니다.

- 전용 장비보다 laptop-first
- 위험한 실제 실험보다 simulation-first
- accelerator 최적화보다 CPU baseline 우선
- vendor lock-in보다 adapter
- mandatory cloud가 아닌 edge-local 실행
- 필요할 때만 Kubernetes/fleet 기능 도입
- 단방향 inference보다 perception-action-feedback loop
- device-specific API보다 stable contract

향후 simulator, model runtime, accelerator, robot, orchestration 기술이 바뀌어도 프로젝트 이름과 핵심 정체성은 유지할 수 있어야 합니다.

더 넓은 프로젝트 방향은 [Siqoq 비전](vision.ko.md)을 참고하세요.
