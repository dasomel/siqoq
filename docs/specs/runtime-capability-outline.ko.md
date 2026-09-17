# 런타임/기능(Capability) 계약 개요

상태: 개요(outline)만 존재합니다. 현재 코드베이스에는 런타임 레지스트리,
검색(discovery) 메커니즘, 강제(enforcement) 수단이 전혀 없습니다. 이
문서는 향후 기능 선언(capability declaration)이 어떤 형태를 취할 수
있는지를 설명하여, Sensor/Semantic Event/Action Contract v0의 소비자들이
특정 런타임이 무엇을 지원하는지에 대해 공유된 어휘를 가질 수 있도록 하는
것이 목적입니다. 후속 이슈 없이 이 개요를 기반으로 강제 메커니즘을 만들지
마십시오 — AGENTS.md의 "가장 작은 일관된 변경"과 "하나의 하드웨어/벤더
경로를 성급하게 고정하지 않기" 규칙을 참고하십시오.

## 동기

`docs/architecture.md`의 배포 모드 표(Laptop / Simulation / Edge / Fleet)는
이미 각 모드가 서로 다른 센서/추론/전송/액션 어댑터의 부분집합을
지원함을 암시하고 있습니다. 기능 선언이 있으면 호출자가 시행착오로
탐색하는 대신(예: `UsbWebcamFrameSensor`의 `NotImplementedError`를 잡는
방식) 런타임이 이를 명시적으로 선언할 수 있습니다.

## 스케치 (예시, 구현되지 않음)

런타임 기능 선언은 작고, 추가적(additive)이며, 순수 데이터 구조가 될 수
있습니다. 예:

```python
@dataclass(slots=True, frozen=True)
class RuntimeCapabilities:
    supports_fixture_sensors: bool = True
    supports_generated_sensors: bool = True
    supports_physical_sensors: bool = False
    supports_mock_actuation_only: bool = True   # 액션 계약 v0 "mock" 검토를 반영
    supports_onnx_inference: bool = False
    supports_transport: tuple[str, ...] = ("in_memory", "stdout", "file")
```

각 필드는 이 코드베이스에 이미 존재하는 계약 개념(센서 계약 v0의 계층,
액션 계약 v0의 `mock` 필드, `siqoq.transport`의 전송 어댑터)에 대응되며,
새로운 범주를 만들어내지 않습니다.

## 배포 모드별 예시 선언

| 모드 | 픽스처 센서 | 생성 센서 | 물리 센서 | mock 전용 액추에이션 | onnx 추론 | 전송 |
|---|---|---|---|---|---|---|
| Laptop | 가능 | 가능 | 불가 | 가능 | 선택적 | in_memory/stdout/file |
| Simulation | 가능 | 가능 | 불가 | 가능 | 선택적 | pluggable |
| Edge | 가능 | 불가 | 가능 | 정책에 따라 다름 | 가능 | nats/mqtt |
| Fleet (계획) | 가능 | 불가 | 가능 | 정책에 따라 다름 | 가능 | managed messaging |

이 표는 오늘 시점에서는 설명적(descriptive)일 뿐입니다
(`docs/architecture.md`의 배포 모드와 일치). 현재 어떤 코드도 이를 읽거나
강제하지 않습니다.

## 이 이슈의 비목표(Non-goals)

- 런타임 레지스트리, 플러그인 검색, 기능 협상(capability negotiation)
  프로토콜을 여기서 추가하지 않습니다.
- 어떤 기존 어댑터도 `RuntimeCapabilities`를 구현하도록 요구하지
  않습니다.
- 이 개요는 CI나 `make verify`를 게이팅하지 않습니다.

후속 이슈는 다음을 범위로 정해야 합니다: 기능을 어디에 선언할지
(어댑터 클래스별 속성 vs. 런타임 레벨 객체), "mock 전용 액추에이션"이
`SafetyGate`와 어떻게 상호작용할지, 기능 불일치 시 즉시 실패해야 할지
우아하게 성능을 낮춰야 할지.
