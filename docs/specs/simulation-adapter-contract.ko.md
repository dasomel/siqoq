# 시뮬레이션 어댑터 계약 v0

상태: v0 (draft) — `siqoq.sensors`의 `CONTRACT_VERSION = 0`과 일치합니다.

이 문서는 `SensorAdapter`(센서 계약 v0, `docs/specs/sensor-contract.md`) 중
무엇이 "실제/녹화" 또는 "물리" 소스가 아니라 "시뮬레이션" 소스인지를
공식화합니다. 이것은 **새로운 프로토콜이 아닙니다**: 시뮬레이션 어댑터는
`SensorAdapter`의 특수화이며, 다른 메서드 시그니처가 아니라 provenance와
CI에 안전한 시뮬레이션 소스가 지켜야 하는 추가적인 결정성(determinism)
보장으로 구분됩니다.

## 무엇이 소스를 "시뮬레이션"으로 만드는가

`SensorAdapter` 구현체는 다음을 만족할 때 *시뮬레이션 어댑터*입니다:

- 물리 센서나 그 녹화본이 아니라, 합성적으로(생성/스크립트/시뮬레이터
  주도) `SemanticEvent`를 생성한다;
- 시맨틱 이벤트 계약 v0의 provenance 컨벤션
  (`docs/specs/semantic-event-contract.ko.md`)에 따라
  `metadata["provenance"] = PROVENANCE_SIMULATED` (`siqoq.events`)로
  태깅한다.

이는 다음과 구분됩니다:

- **recorded** (`PROVENANCE_RECORDED`): 이전에 캡처된 데이터를 재생합니다
  (예: JSONL 픽스처를 읽는 `FixtureSensorAdapter`). Recorded 소스는 파일
  내용이 고정되어 있어 구조적으로 결정적이지만, 아무것도 합성하지 않으므로
  "시뮬레이션"은 아닙니다.
- **physical** (`PROVENANCE_PHYSICAL`): 실제 물리 센서를 읽습니다. 결정적일
  수 없으며, 테스트 어설션의 근거로 CI에 안전하지 않습니다.

`GeneratedSensorAdapter`는 참조 시뮬레이션 어댑터 구현체입니다:
`SensorAdapter`를 만족하며 `FixtureSensorAdapter`와 동일한 conformance
스위트(`tests/test_sensors.py`)로 검증됩니다. 계약 레벨에서는 둘 다 그냥
평범한 `SensorAdapter`이기 때문입니다.

## CI에 안전한 시뮬레이션 어댑터의 결정성 요구사항

CI가 회귀 어설션에 의존하는 시뮬레이션 어댑터는 **동일 입력 -> 동일
출력**을 실행/머신 간에 바이트 단위로 반드시 만족해야 합니다. 구체적으로:

- 해시되거나 비교되는 어떤 값에도 wall-clock이 유입되어서는 안 됩니다.
  이는 `siqoq.scenario`에 이미 적용된 패턴과 동일합니다:
  `ScenarioSummary.duration_seconds`는 wall-clock 값이며 `sequence_hash`
  계산에서 명시적으로 제외됩니다(`_sequence_hash`는 타이밍이 아니라 이벤트
  payload만 해시합니다), 그리고 "벤치마크 측정이 아니라 대략적인 CI
  정상성 신호일 뿐"이라고 문서화되어 테스트에서 엄격한 범위를 어설션하지
  않도록 되어 있습니다. 시뮬레이션 어댑터는 해시/JSON 비교/실행 간 동등성
  어설션에 사용되는 필드에 새로운 wall-clock 기반 값(예: `datetime.now()`)을
  유입시켜서는 안 됩니다.
- 시뮬레이션 어댑터가 방출하는 시간에 따라 변하는 필드(예: `timestamp`)는,
  재현 가능한 출력이 필요한 컨텍스트(테스트, 시나리오 벤치마크)에서는
  주변 clock 상태가 아니라 호출자가 명시적으로 제공한 파라미터로 완전히
  결정되어야 합니다. "설정되지 않으면 현재 시간을 사용"과 같은 비결정적
  기본값은 호출자가 고정값을 선택하지 않은 경우에만 허용되며, 어떤 CI
  어설션도 이에 의존해서는 안 됩니다.
- 동일한 생성 파라미터와 동일한 `read(count=N)` 호출에 대해, 독립적인 두
  번의 실행은 동일한 `SemanticEvent` 시퀀스(순서대로 동일한 `to_json()`
  출력)를 반환해야 합니다.

`GeneratedSensorAdapter`는 오늘 이를 `timestamp: str | None` 필드로
만족합니다: 호출자가 고정된 `timestamp`를 전달하면 `read()`가 반환하는
모든 이벤트가 주변 clock 시간이 아니라 그 정확한 값을 가지게 되어, 실행
간 바이트 단위로 재현 가능한 출력을 만듭니다. 이는
`tests/test_sensors.py::test_adapter_is_deterministic_with_fixed_timestamp`와
`test_generated_adapter_is_deterministic_and_simulated_provenance_ready`로
검증됩니다.

## 시뮬레이터 SDK 격리

향후 시뮬레이터 브리지(예: Isaac Sim, Gazebo)는 시뮬레이터 전용 SDK
타입을 `SensorAdapter`나 `SemanticEvent`의 시그니처에 유입시켜서는 안
됩니다. 브리지 어댑터의 `read()` 메서드는 오늘날의
`GeneratedSensorAdapter`/`FixtureSensorAdapter`와 정확히 동일하게,
정규화된 Python 원시 타입(`str`, `float`, `dict`)으로 구성된 순수한
`SemanticEvent` 인스턴스를 반환해야 합니다. 시뮬레이터 SDK 객체(scene
핸들, 센서 프록시, 물리 엔진 타입 등)는 어댑터의 구현 내부에만 머물러야
하며, `SensorAdapter`/`SemanticEvent`의 파라미터 타입, 반환 타입, 필드
타입으로 절대 등장해서는 안 됩니다. 이는 `docs/specs/sensor-contract.md`의
기존 프레임 레벨 규칙("벤더 SDK 타입은 이 계약에 등장하지 않습니다")을
그대로 따르는 것입니다.

## 호환성 규칙

센서 계약 v0(`docs/specs/sensor-contract.md#호환성-규칙`)과 동일합니다:
이 문서는 기존 `SensorAdapter` 프로토콜 위에 보장을 추가할 뿐 메서드
시그니처를 변경하지 않으므로 `CONTRACT_VERSION` 증가가 필요하지 않습니다.
위 결정성 보장을 약화시키는 향후 변경(예: 기본적으로 해시된 출력에
wall-clock 유입을 허용)은 호환성 파괴로 취급됩니다.

## Conformance

- `tests/test_sensors.py`는 `GeneratedSensorAdapter`를 공유
  `SensorAdapter` conformance 스위트(센서 계약 v0)로 검증하며, 이 문서를
  위한 전용 결정성/provenance 준비 테스트도 포함합니다.
- `siqoq.scenario._sequence_hash`는 wall-clock 없이 CI에 안전한 해시를
  계산하는 정석적인 예시입니다.
