# 결정론적 시나리오

[English](scenarios.md) | **한국어**

Siqoq은 전체 simulator나 실제 hardware를 연결하기 전에 가벼운 deterministic fixture를 사용합니다. 이 fixture는 recorded video, Isaac Sim, Gazebo, 실제 sensor를 대체하기 위한 것이 아니라, Siqoq의 contract와 perception-action 흐름을 모든 CI architecture에서 빠르게 검증하기 위한 regression layer입니다.

## 현재 fixture 형식

초기 형식은 UTF-8 JSONL입니다. 비어 있지 않은 각 줄은 하나의 정규화된 `SensorSample`을 나타냅니다.

```json
{"source":"fixture.camera.front","kind":"image","timestamp":"2026-01-01T00:00:00+00:00","sequence":0,"payload":{"frame":"frame-000"},"metadata":{"origin":"fixture"}}
```

초기 fixture에는 작은 logical payload만 저장합니다. 실제 이미지/영상 같은 binary 데이터는 이후 recorded-media adapter와 artifact reference 방식으로 처리하며, semantic event나 기본 regression fixture에 큰 blob을 직접 넣지 않는 방향을 유지합니다.

## 첫 시나리오 실행

```bash
siqoq scenario examples/scenarios/person-detection.jsonl --name person-detection
```

명령은 scenario 이름, 처리 sample 수, semantic event 수, action result 수, 거부된 action 수, host architecture를 포함한 machine-readable JSON summary를 출력합니다.

## 초기 실행 흐름

```text
JSONL SensorSample fixture
          ↓
JsonlFixtureSensor
          ↓
StaticInference
          ↓
SemanticEvent
          ↓
DetectionRulePolicy
          ↓
AllowListSafetyGate
          ↓
MockActionAdapter
          ↓
ScenarioSummary
```

이 경로는 network, broker, camera, GPU, ROS 2, robot 없이도 이후 실제 integration이 지켜야 할 동일한 boundary를 검증합니다.

## Conformance

`GeneratedSensor`와 `JsonlFixtureSensor`는 동일한 lightweight Sensor Contract conformance helper를 통해 검증합니다. 이는 #17에서 추진하는 정식 adapter conformance suite의 첫 executable 단계입니다.

## CI 역할

Scenario command는 Linux AMD64, Linux ARM64, macOS AMD64, macOS ARM64에서 모두 실행합니다. 따라서 hardware-specific job을 추가하기 전에도 logic regression과 기본적인 cross-platform assumption을 함께 검증할 수 있습니다.

## 다음 단계

- deterministic media fixture를 사용하는 recorded-video adapter
- 실제 webcam adapter
- OpenCV + ONNX Runtime baseline
- versioned formal schema
- scenario assertion / benchmark metadata
- optional JSONL event artifact
- 이후 fast default gate와 분리된 simulator-heavy regression job
