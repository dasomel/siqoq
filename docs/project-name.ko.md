# 프로젝트 이름 — Siqoq

[English](project-name.md) | **한국어**

## 발음

Siqoq은 이 프로젝트에서 **“시콕”**이라고 읽습니다.

## 뜻과 프로젝트에서의 의미

Siqoq이라는 이름은 북극권의 눈과 바람, 특히 **바람을 따라 흩날리며 이동하는 눈(drifting snow)**의 이미지에서 영감을 받았습니다.

프로젝트에서는 이 이미지를 다음과 같이 해석합니다.

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

향후 simulator, model runtime, accelerator, robot, orchestration 기술이 바뀌어도 프로젝트 이름과 핵심 정체성은 유지할 수 있어야 합니다.
