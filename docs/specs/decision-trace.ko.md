# 결정 추적(Decision Trace) v0

상태: v0 (`src/siqoq/trace.py`, #11의 일부).

`DecisionTrace`는 센서 입력 -> 시맨틱 이벤트 -> 정책 결정 -> 액션 결과에
이르는 하나의 추적 가능한 레코드를, `SemanticEvent`(`events.py`)와
`ActionResult`(`actuation.py`)가 이미 가지고 있는 `correlation_id` 연결
정보를 사용해 조립합니다. 이는 파이프라인의 다른 곳에서 이미 생성된
데이터를 읽기 전용으로 조합하는 뷰일 뿐이며, 스스로 센서를 관찰하거나
정책을 실행하거나 액션을 수행하지 않습니다.

## 필드

```python
@dataclass(slots=True, frozen=True)
class DecisionTrace:
    correlation_id: str | None
    event_type: str
    event_source: str
    event_confidence: float
    event_timestamp: str
    action: str | None
    action_outcome: str | None
    action_timestamp: str | None
    metadata: dict[str, Any] | None = None
```

`build_trace(event, result=None, *, include_metadata=False)`는
`SemanticEvent`와 선택적인 `ActionResult`로부터 추적 레코드를 만듭니다.
`correlation_id`로 "연관"시킨다는 것은, 호출자가 이미 매칭된 쌍(예:
같은 파이프라인 실행에서 나온 이벤트/결과)을 넘겨준다는 의미입니다.
여러 이벤트/결과 목록에서 일치하는 것을 찾는 검색은 수행하지 않으며,
로그 전체에서 매칭이 필요한 호출자는 `build_trace()`를 호출하기 전에
직접 그 매칭을 해야 합니다.

## 기본 리덕션(redaction)

**기본값(`include_metadata=False`)에서는 `event.metadata`에 내용이
있어도 `DecisionTrace.metadata`는 항상 `None`입니다.** 이는 이슈에서
요구한 기본 리덕션입니다: `SemanticEvent.metadata`는 자유 형식(dict)
필드이므로, 프로듀서가 원본 센서 페이로드(예: 카메라 프레임, 원본
오디오 버퍼)를 여기에 넣을 수 있습니다. 결정 추적 레코드는 RCA를 위해
읽기 쉽고 공유 가능하며 로그로 남겨도 안전해야 하며, 그 원본 페이로드를
절대 함께 실어 날라서는 안 됩니다.

따라서 기본 추적 레코드에는 다음만 포함됩니다:

- `event_type`, `event_source`, `event_confidence`, `event_timestamp` —
  무엇이, 어떤 소스에서, 어느 확신도로, 언제 감지되었는지;
- `action`, `action_outcome`, `action_timestamp` — 어떤 액션이 뒤따랐는지,
  그 결과가 무엇이었는지(`actuation.py` 기준 `"executed"` /
  `"rejected"` / `"noop"`), 그리고 언제였는지;
- `correlation_id` — 이 추적 레코드를 다른 로그의 원본 이벤트/액션 쌍과
  연결하기 위한 값.

이는 원본 센서 바이트를 절대 포함하지 않으면서도, 무엇이 감지되었고
얼마나 확신했으며 시스템이 무엇을 하기로 결정했고 결과가 무엇이었는지에
대한 근본 원인 분석(RCA)에 충분한 컨텍스트를 의도적으로 제공합니다.

## 상세(verbose) 옵트인

`build_trace()`에 `include_metadata=True`를 넘기면 `event.metadata`가
그대로 `DecisionTrace.metadata`에 복사됩니다. 이는 명시적으로 상세하고
비기본값인 디버깅 모드입니다: 옵트인한 호출자(운영자 또는 디버깅 도구)는
프로듀서가 `metadata`에 넣은 원본/민감 데이터가 결과 추적 레코드와,
그 추적 레코드가 로그로 남겨지거나 출력되는 모든 곳에 나타날 수 있음을
받아들이는 것입니다. 기본 로깅 경로에서는 이 옵션을 활성화하지 마십시오.

## `to_json()`

`SemanticEvent.to_json()` / `ActionResult.to_json()`와 동일한
추가 전용(additive-only), 값이 없으면 생략(omit-if-empty) 방식을
따릅니다: `correlation_id`, `action`, `action_outcome`,
`action_timestamp`, `metadata`는 `None`일 때 JSON 페이로드에서
생략됩니다.

## CLI

```
siqoq trace build --event-json <path> [--action-json <path>] [--include-metadata]
```

`SemanticEvent` JSON 문서(및 선택적으로 `ActionResult` JSON 문서)를
읽어 조립된 `DecisionTrace`를 JSON으로 출력합니다. `--include-metadata`는
위의 상세 옵트인을 활성화합니다.

## 호환성 규칙

- **호환성 깨짐(Breaking)**: `DecisionTrace` 필드를 제거/이름 변경하거나,
  `include_metadata`의 기본값을 `False`가 아닌 값으로 바꾸는 경우
  (그 기본값 자체가 이 계약이 보장하는 리덕션입니다).
- **호환 가능/추가적(Compatible / additive)**: 기본값이 있는 새
  `DecisionTrace` 필드를 추가하거나, `build_trace()`에 새로운 선택적
  키워드 파라미터를 추가하는 경우.
