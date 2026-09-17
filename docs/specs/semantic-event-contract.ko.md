# 시맨틱 이벤트 계약 v0

상태: v0 (`siqoq.events`의 `SCHEMA_VERSION = 1`. 계약 자체는 "v0"으로
버전이 매겨지며, 와이어 스키마 버전 정수는 `1`입니다 — 아래 "버전 관리
참고" 참조).

`SemanticEvent`는 추론/센서 어댑터와 다운스트림 정책/전송 코드 사이의
안정적인 경계입니다 (`docs/architecture.md`의 "시맨틱 이벤트 계층" 참고).

## 필수 필드

`REQUIRED_FIELDS = ("type", "source", "object", "confidence", "timestamp", "schema_version")`

- `type: str` — 이벤트 종류, 예: `"object.detected"`.
- `source: str` — 생산자 식별자, 예: `"sim.camera.front"`,
  `"file.video.recorded"`.
- `object: str` — 탐지/관찰된 대상.
- `confidence: float` — `[0, 1]` 범위.
- `timestamp: str` — ISO 8601 형식.
- `schema_version: int` — 이 이벤트가 생성될 때의 `SCHEMA_VERSION`.

## 선택 필드

`OPTIONAL_FIELDS = ("correlation_id", "metadata")`

- `correlation_id: str | None` — 파이프라인 단계 전체에서 하나의 탐지를
  추적하기 위한 값.
- `metadata: dict[str, Any]` — 벤더에 종속되지 않는 자유 형식의 추가
  컨텍스트. `to_json()`은 값이 비어 있거나 `None`이면 두 선택 필드를 완전히
  생략하므로, 필수 키만 읽는 기존 소비자는 이 필드들의 존재 여부에 영향을
  받지 않습니다.

## Provenance 메타데이터 (시뮬레이션 vs. 실제/녹화)

이 스펙에서 새로 추가된, 순수 추가(additive-only) 항목입니다: 생산자는
`siqoq.events`가 제공하는 다음 상수 중 하나를 `metadata["provenance"]`에
설정하는 것을 권장(SHOULD)합니다:

- `PROVENANCE_SIMULATED = "simulated"` — 합성/생성 데이터
  (`GeneratedSensorAdapter`).
- `PROVENANCE_RECORDED = "recorded"` — 픽스처/녹화 데이터
  (`FixtureSensorAdapter`, `RecordedVideoFileSensor`).
- `PROVENANCE_PHYSICAL = "physical"` — 실시간 물리 센서.

이는 *기존 `metadata` 딕셔너리에 대한 관례*이며 새로운 필수 필드가
아닙니다. 따라서 `SCHEMA_VERSION`을 올릴 필요가 없습니다. provenance가
필요한 소비자는 이 값이 없을 수도 있음(오래된/비준수 생산자)을
허용해야(MUST) 하며, 필수 값으로 취급해서는 안 됩니다.

## 벤더 중립성

`SemanticEvent`의 필드 타입이나 `siqoq.events`의 공개 API 어디에도 OpenCV
(`cv2`), ONNX Runtime (`onnxruntime`), NATS, MQTT 타입이 등장하지 않습니다
— 모든 필드는 Python 기본 타입(`str`, `float`, `int`, `dict`)입니다. 벤더
SDK를 감싸는 어댑터(예: `OnnxCvInferenceAdapter`)는 자신의 경계에서 이
계약으로 변환하며, 계약 모듈 자체는 벤더 SDK를 절대 import하지 않습니다.

## 호환성 규칙

- **호환성 파괴 (Breaking, `SCHEMA_VERSION` 증가 필요)**: 필수 필드 제거
  또는 이름 변경, 필수 필드의 타입이나 유효 값 범위 변경, `to_json()`의 키
  *의미* 변경(값 형태가 동일해도 키 이름을 바꾸는 것은 breaking입니다).
- **호환/추가적 (Additive, 증가 불필요)**: 새 선택 필드 추가, 위
  `provenance`와 같은 새로운 `metadata` 키 관례 추가, 새로운 `type` 값
  추가, 키 순서가 다르지만 동일한 키를 가진 JSON 페이로드에 의존하는 것
  (`to_json()`은 키 순서를 절대 보장하지 않습니다).

## 버전 관리 참고

계약 레벨 레이블("v0")과 와이어 레벨 `SCHEMA_VERSION` 정수(`1`)는
의도적으로 분리되어 있습니다: `SCHEMA_VERSION`은 이슈 #17 이전부터 이미
존재했으며, 불필요하게 breaking처럼 보이는 diff를 피하기 위해 여기서
재번호를 매기지 않았습니다. 향후 계약 개정은 위 규칙에 따라
`SCHEMA_VERSION`을 올리며, 스펙 문서의 버전 레이블도 동일하게 증가합니다.
