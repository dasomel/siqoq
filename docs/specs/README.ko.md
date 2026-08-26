# Siqoq Contract Specification

[English](README.md) | **한국어**

Siqoq은 구현 core는 작게 유지하되 경계는 명확하게 정의하는 것을 목표로 합니다. 이 디렉터리는 simulation, laptop, edge, physical system 사이를 연결하는 **안정적이고 versioned된 contract**를 관리합니다.

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
- event type / source
- confidence / model provenance
- correlation / trace ID
- timestamp
- 큰 raw artifact는 event body에 직접 넣기보다 reference 사용

### Action Contract

Reasoning/policy가 실제 physical execution으로 넘어가기 전에 사용하는 request/result contract를 정의합니다.

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

### Capability Contract

Edge node, simulator, adapter가 무엇을 제공할 수 있는지 vendor-specific API를 core scheduler/runtime에 노출하지 않고 표현합니다.

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
