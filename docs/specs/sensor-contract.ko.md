# 센서 계약 v0

상태: v0 (draft) — `siqoq.sensors`와 `siqoq.video_sensors`의
`CONTRACT_VERSION = 0`과 일치합니다.

Siqoq은 두 개의 센서 계약 계층을 가지고 있습니다. 서로 경쟁하는 추상화가
아니며, 각각 다른 경계를 담당하고 보통 한 계층 위에 다른 계층을 조합해서
사용합니다.

## 계층 1: 이벤트 레벨 (`siqoq.sensors.SensorAdapter`)

```python
class SensorAdapter(Protocol):
    def read(self, *, count: int) -> Iterator[SemanticEvent]: ...
```

v0 보장 사항:

- `read(count=N)`은 순서를 유지하며 최대 `N`개의 `SemanticEvent`를 반환합니다.
- 반환되는 모든 이벤트는 시맨틱 이벤트 계약 v0
  (`docs/specs/semantic-event-contract.ko.md`)을 만족합니다: `type`,
  `source`, `object`, `confidence`, `timestamp`, `schema_version`이 존재하고,
  `confidence`는 `[0, 1]` 범위의 `float`이며, `source`/`object`/`timestamp`는
  비어 있지 않은 문자열입니다.
- 정상 입력에 대해서는 예외를 던지지 않아야 합니다. 잘못된 픽스처 입력은
  문제가 된 줄 번호를 포함한 `ValueError`를 발생시킵니다
  (`FixtureSensorAdapter` 참고).
- `GeneratedSensorAdapter`(합성/시뮬레이션)와 `FixtureSensorAdapter`(녹화
  데이터) 모두 동일한 계약을 구현하며 동일한 conformance 테스트 스위트
  (`tests/test_sensors.py`)로 검증됩니다.

## 계층 2: 프레임 레벨 (`siqoq.video_sensors.FrameSensor`)

```python
class FrameSensor(Protocol):
    def open(self) -> None: ...
    def read(self) -> Frame | None: ...
    def close(self) -> None: ...
```

v0 보장 사항:

- 명시적인 생명주기: `read()` 전에 반드시 `open()`을 호출해야 하고, 소스가
  끝나면 `read()`는 예외 대신 `None`을 반환합니다. `close()`는 소스 종료 후
  다시 호출해도 안전합니다.
- `Frame`은 정규화된 `FrameMetadata`(source, index, timestamp, width, height,
  format)와 원시 `payload: bytes`로 구성됩니다. 벤더 SDK 타입(예: OpenCV
  `Mat`, 코덱 전용 프레임 객체)은 이 계약에 등장하지 않습니다.
- `FrameSensor` 구현체(`RecordedVideoFileSensor`, `MockWebcamFrameSensor`,
  `UsbWebcamFrameSensor`)는 `SensorAdapter`보다 더 낮은 계층입니다: 프레임
  생산자는 보통 `InferenceAdapter`(`siqoq.inference`)와 결합되어
  `SensorAdapter`가 반환하는 `SemanticEvent`로 변환됩니다. 현재 Siqoq은
  `FrameSensor + InferenceAdapter -> SensorAdapter` 브리지를 기본 제공하지
  않으며, 이를 추가하는 것은 호환성을 깨지 않는 후속 작업입니다.

## 두 계층의 관계

```text
FrameSensor (프레임 레벨)  --InferenceAdapter-->  SemanticEvent  <--반환--  SensorAdapter (이벤트 레벨)
```

`SensorAdapter`는 정책/전송 코드 대부분이 의존해야 하는 안정적인 상위
계약입니다. `FrameSensor`가 별도로 존재하는 이유는 일부 소스(녹화 영상,
웹캠)가 미리 분류된 이벤트가 아니라 프레임을 자연스럽게 생성하기 때문이며,
분리해 둠으로써 추론 백엔드(mock vs. ONNX/OpenCV)를 이벤트 레벨 계약을
건드리지 않고 교체할 수 있습니다.

## 호환성 규칙

- **호환성 파괴 (Breaking, `CONTRACT_VERSION` 증가 필요)**: 프로토콜 메서드
  제거/이름 변경, `read()`의 반환 의미 변경(예: 소스 종료 시 `None` 반환
  대신 예외를 던지도록 변경), `FrameMetadata`/`Frame`의 필수 필드 제거, 필수
  필드가 가질 수 있는 값의 범위를 축소하는 변경.
- **추가적/호환 (Additive, 증가 불필요)**: 기본값이 있는 새 키워드 전용
  선택 파라미터, `FrameMetadata`의 새 선택 필드, 새로운
  `SensorAdapter`/`FrameSensor` 구현체, 문서만 수정하는 명확화.

## Conformance

`tests/test_sensors.py`는 공유 conformance 스위트를 `GeneratedSensorAdapter`
(가짜/시뮬레이션)와 `FixtureSensorAdapter`(실제/녹화 픽스처 데이터)에 대해
파라미터화하여, 일반적인 어댑터 동작과 위 센서 계약 v0의 필드/형태 보장을
모두 검증합니다.

## 파이프라인 레벨 호환성 (Phase 2)

위 어댑터 레벨 conformance 스위트는 `GeneratedSensorAdapter`와
`FixtureSensorAdapter`가 동일한 `SensorAdapter` 프로토콜을 만족함을
증명합니다. 하지만 이것만으로는 Phase 2의 인수 조건, 즉 "동일한 다운스트림
파이프라인이 시뮬레이션 입력과 실제 카메라 입력을 모두 소비한다"를
충족하기에 충분하지 않습니다 — 파이프라인(`siqoq.scenario.run_scenario`)
자체가 어떤 어댑터를 받았는지에 따라 분기하지 않는다는 것을 보여주지는
않기 때문입니다.

`tests/test_scenario.py::test_build_adapter_is_the_only_dispatch_point_on_adapter_type`는
`run_scenario`의 소스를 검사하여 `ScenarioConfig.build_adapter()`가
`adapter`/소스 타입에 대해 분기하는 유일한 지점임을 검증하고, `run_scenario`
자체는 공유 프로토콜을 통해 `adapter.read()`를 정확히 한 번만 호출함을
확인합니다.
`tests/test_scenario.py::test_run_scenario_pipeline_shape_matches_across_generated_and_fixture_sources`는
`ScenarioConfig(adapter="generated", ...)`와
`ScenarioConfig(adapter="fixture", source_path=..., ...)`에 대해 동일한
`run_scenario()` 호출을 실행하고, 두 결과 모두 동일한 필드 구성과 형태
(`event_count`, `type_counts` 키, `action_counts` 키)의 `ScenarioSummary`를
생성함을 검증합니다. 이 두 테스트가 함께 Phase 2의 인수 조건을 어댑터
경계뿐 아니라 파이프라인 전체에서 충족함을 보여줍니다.
