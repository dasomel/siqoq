# Siqoq Contract Specification

[English](README.md) | **한국어**

Siqoq은 구현 core는 작게 유지하되 경계는 명확하게 정의하는 것을 목표로 합니다. 이 디렉터리는 simulation, laptop, edge, physical system 사이를 연결하는 **안정적이고 versioned된 contract**를 관리합니다.

## 현재 구현된 스켈레톤

첫 code-level contract skeleton은 다음 파일에 들어가 있습니다.

- `src/siqoq/contracts.py` — `SensorSample`, `Detection`, `ActionRequest`, `ActionResult`, `DeviceCapabilities` 및 adapter protocol
- `src/siqoq/events.py` — versioned `SemanticEvent` envelope
- `src/siqoq/pipeline.py` — perception → event → policy → safety → action 흐름
- `src/siqoq/adapters.py` — generated sensor, static inference, in-memory transport, allow-list safety gate, mock action adapter
- `src/siqoq/runtime.py` — runtime manifest와 dependency-free capability discovery

이 구현들은 향후 public API를 확정한 것이 아니라 **확장 가능한 최소 골격**입니다. Issue #17에서 versioned specification과 공통 adapter conformance suite로 발전시킵니다.

## 예정된 명세

### Sensor Contract

Simulator/vendor API에 종속되지 않는 sensor sample과 lifecycle을 정의합니다.

초기 범위:

- source identity / capability metadata
- timestamp / sequence number
- 특정 image transport를 강제하지 않는 frame metadata
- health/readiness state
- simulated/physical provenance
- optional calibration metadata

### Semantic Event Contract

Detection, classification, tracking, anomaly, state change 같은 model-independent perception event를 정의합니다.

초기 범위:

- versioned envelope
- event ID / type / source
- confidence / model provenance
- correlation / trace ID
- timestamp / source sequence
- 큰 raw artifact는 event body에 직접 넣기보다 reference 사용

### Action Contract

Reasoning/policy가 실제 physical execution으로 넘어가기 전에 사용하는 request/result contract를 정의합니다.

```text
Decision
  ↓
ActionRequest
  ↓
SafetyGate
  ↓
ActionAdapter
  ↓
Physical hardware
```

현재 스켈레톤은 safe-by-default입니다. `NoOpPolicy`는 action을 만들지 않고, `AllowListSafetyGate`는 명시적으로 허용하지 않은 action을 모두 거부하며, `MockActionAdapter`는 실제 hardware를 전혀 건드리지 않습니다.

초기 범위:

- action type / target
- requested parameters
- constraints / expiration
- policy/safety decision
- execution status/result
- correlation / audit metadata

### Runtime Manifest

Siqoq workload를 portable하게 선언하는 형식을 정의합니다.

예상 항목:

- sensor requirements
- model/runtime requirements
- CPU/GPU/accelerator constraints
- transport configuration
- telemetry configuration
- action capability
- deployment profile

현재 `RuntimeManifest`는 laptop profile bootstrap을 제공하고 `siqoq inspect` 명령으로 확인할 수 있습니다.

### Capability Contract

Edge node, simulator, adapter가 무엇을 제공할 수 있는지 vendor-specific API를 core scheduler/runtime에 노출하지 않고 표현합니다.

현재 dependency-free bootstrap은 host architecture만 탐지하고 accelerator/sensor/actuator는 vendor-specific probe가 추가되기 전까지 비워 둡니다.

## Versioning 원칙

- 필요한 경우 contract version을 implementation package와 독립적으로 관리
- additive/compatible change 우선
- vendor SDK type을 core schema에 포함하지 않음
- 큰 binary sensor payload는 semantic event에 직접 포함하기보다 reference 사용
- safety-sensitive action field는 compatibility review 필수
- simulator와 physical implementation은 같은 conformance test를 공유

## Conformance 원칙

Adapter가 단순히 실행된다고 지원 완료로 보지 않습니다. 공통 contract conformance suite를 통과해야 supported adapter로 간주합니다.

```text
RecordedVideoAdapter ─┐
WebcamAdapter ────────┼─→ Sensor Contract Conformance
IsaacSimAdapter ──────┤
ROS2CameraAdapter ────┘
```

이 구조가 Siqoq의 simulation-to-reality portability를 검증하는 핵심 기반이 됩니다.
